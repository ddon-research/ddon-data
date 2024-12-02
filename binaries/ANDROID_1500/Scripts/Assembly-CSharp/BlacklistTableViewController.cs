using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using WebRequest;

public class BlacklistTableViewController : TableViewController<BlacklistTableViewController.BlackListData>
{
	public class BlackListData
	{
		public bool IsBlock;

		public MemberListData data { get; private set; }

		public BlackListData(MemberListData mem)
		{
			data = mem;
			IsBlock = false;
		}
	}

	[SerializeField]
	private Text SelectedText;

	[SerializeField]
	protected bool BlacklistIsPosting;

	protected object BlacklistthisLock = new object();

	private void LoadData()
	{
		TableData.Clear();
		StartCoroutine(Clan.GetMember(delegate(ClanMemberList resClanMembers)
		{
			foreach (ClanMemberListElement member in resClanMembers.Members)
			{
				MemberListData memberListData = new MemberListData();
				memberListData.SetFromPacket(member);
				memberListData.IsClanMember = true;
				if (resClanMembers.OnlineCharacterIDs.Contains(member.CharacterID))
				{
					memberListData.IsOnline = true;
				}
				uint characterID = SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData.CharacterID;
				if (characterID != memberListData.CharacterId)
				{
					TableData.Add(new BlackListData(memberListData));
				}
			}
			StartCoroutine(WebRequest.AppBlackList.GetList(delegate(AppBlackListParam blackParam)
			{
				Dictionary<uint, Packet.AppBlackList> dictionary = new Dictionary<uint, Packet.AppBlackList>();
				foreach (Packet.AppBlackList black in blackParam.BlackList)
				{
					dictionary[black.RegisteredCharactersId] = black;
				}
				foreach (BlackListData tableDatum in TableData)
				{
					uint characterId = tableDatum.data.CharacterId;
					if (dictionary.ContainsKey(characterId))
					{
						tableDatum.IsBlock = true;
					}
				}
				UpdateContents();
				ShowCountingBlockNum();
			}, delegate(UnityWebRequest result)
			{
				AppUtility.ShowErr(result.downloadHandler.text, "AppBlackList");
			}, null, LoadingAnimation.Default));
		}, null, null, LoadingAnimation.Default));
	}

	protected override float CellHeightAtIndex(int index)
	{
		return 135f;
	}

	protected override void Awake()
	{
		base.Awake();
	}

	protected override void Start()
	{
		base.Start();
	}

	private void OnEnable()
	{
		LoadData();
		BlacklistIsPosting = false;
	}

	private void PostBlackList()
	{
		AppBlackListParam appBlackListParam = new AppBlackListParam();
		foreach (BlackListData tableDatum in TableData)
		{
			appBlackListParam.BlackList.Add(new Packet.AppBlackList(tableDatum.data.CharacterId, !tableDatum.IsBlock));
		}
		lock (BlacklistthisLock)
		{
			if (BlacklistIsPosting)
			{
				return;
			}
			BlacklistIsPosting = true;
		}
		StartCoroutine(WebRequest.AppBlackList.PostList(delegate
		{
			SingletonMonoBehaviour<AppUtility>.Instance.ShowDialogAndPop("完了確認", "ブラックリストを保存しました。");
			BlacklistIsPosting = false;
		}, delegate(UnityWebRequest result)
		{
			AppUtility.ShowErr(result.downloadHandler.text, "AppBlackList");
			BlacklistIsPosting = false;
		}, appBlackListParam, LoadingAnimation.Default));
	}

	public void CheckPostBlackList()
	{
		SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK_Cancel, "確認", "ブラックリストを保存しますか？", delegate(ModalDialog.Result res)
		{
			if (res == ModalDialog.Result.OK)
			{
				PostBlackList();
			}
		});
	}

	public void ShowCountingBlockNum()
	{
		int count = TableData.Count;
		int num = 0;
		foreach (BlackListData tableDatum in TableData)
		{
			if (tableDatum.IsBlock)
			{
				num++;
			}
		}
		SelectedText.text = num + "/" + count;
	}
}
