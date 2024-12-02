using System.Collections;
using System.Collections.Generic;
using System.Linq;
using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class MemberListTableViewController : TableViewController<MemberListData>
{
	public enum DataSourceType
	{
		Clan,
		Friend,
		Online
	}

	[SerializeField]
	private DataSourceType SourceType;

	[SerializeField]
	private Text SelectedNumText;

	[SerializeField]
	private Text EmptyText;

	public Dictionary<uint, MemberListData> SelectedMemberList = new Dictionary<uint, MemberListData>();

	private void LoadData()
	{
		TableData.Clear();
		StartCoroutine(GetMemberList());
	}

	private IEnumerator GetMemberList()
	{
		SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		if (EmptyText != null)
		{
			EmptyText.enabled = false;
		}
		if (SourceType == DataSourceType.Clan)
		{
			yield return GetClanMember();
			yield return GetFriend();
		}
		else
		{
			yield return GetFriend();
			yield return GetClanMember();
		}
		if (EmptyText != null && TableData.Count <= 0)
		{
			EmptyText.enabled = true;
		}
		UpdateContents();
		SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
	}

	private IEnumerator GetClanMember()
	{
		yield return Clan.GetMember(delegate(ClanMemberList resClanMembers)
		{
			foreach (ClanMemberListElement member in resClanMembers.Members)
			{
				bool flag = false;
				foreach (MemberListData tableDatum in TableData)
				{
					if (tableDatum.CharacterId == member.CharacterID)
					{
						tableDatum.IsClanMember = true;
						tableDatum.ClanMemberRank = member.MemberRank;
						flag = true;
						break;
					}
				}
				if (!flag)
				{
					MemberListData memberListData = new MemberListData();
					memberListData.SetFromPacket(member);
					memberListData.IsClanMember = true;
					memberListData.ClanMemberRank = member.MemberRank;
					if (SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData != null && memberListData.CharacterId == SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData.CharacterID)
					{
						memberListData.IsMine = true;
					}
					if (resClanMembers.OnlineCharacterIDs.Contains(member.CharacterID))
					{
						memberListData.IsOnline = true;
					}
					if (SourceType == DataSourceType.Clan)
					{
						TableData.Add(memberListData);
					}
					else if (SourceType == DataSourceType.Online && memberListData.IsOnline)
					{
						TableData.Add(memberListData);
					}
				}
			}
		}, null, CacheOption.OneMinute);
	}

	private IEnumerator GetFriend()
	{
		yield return Friend.GetMember(delegate(CharacterMemberList resFriends)
		{
			foreach (CharacterMemberListElement member in resFriends.Members)
			{
				bool flag = false;
				foreach (MemberListData tableDatum in TableData)
				{
					if (tableDatum.CharacterId == member.CharacterID)
					{
						tableDatum.IsFriend = true;
						flag = true;
						break;
					}
				}
				if (!flag)
				{
					MemberListData memberListData = new MemberListData();
					memberListData.SetFromPacket(member);
					memberListData.IsFriend = true;
					if (resFriends.OnlineCharacterIDs.Contains(member.CharacterID))
					{
						memberListData.IsOnline = true;
					}
					if (SourceType == DataSourceType.Friend)
					{
						TableData.Add(memberListData);
					}
					else if (SourceType == DataSourceType.Online && memberListData.IsOnline)
					{
						TableData.Add(memberListData);
					}
				}
			}
		}, null, CacheOption.OneMinute);
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
		if (SingletonMonoBehaviour<NavigationViewController>.Instance.PrevNavigationDir == NavigationViewController.NavigationDir.Back)
		{
			return;
		}
		SelectedMemberList.Clear();
		Dictionary<uint, MemberListData> memberList = SingletonMonoBehaviour<MailSendManager>.Instance.GetMemberList();
		foreach (KeyValuePair<uint, MemberListData> item in memberList)
		{
			SelectedMemberList.Add(item.Key, item.Value);
		}
		if (SelectedNumText != null)
		{
			SelectedNumText.text = SelectedMemberList.Count().ToString();
		}
		Initialize();
		LoadData();
	}

	public void OnPressCell(MainMenuTableViewCell cell)
	{
	}

	public bool AddMember(MemberListData data)
	{
		if (!SelectedMemberList.ContainsKey(data.CharacterId))
		{
			SelectedMemberList.Add(data.CharacterId, data);
			if (SelectedNumText != null)
			{
				SelectedNumText.text = SelectedMemberList.Count().ToString();
			}
			return true;
		}
		return false;
	}

	public bool RemoveMember(uint characterId)
	{
		if (SelectedMemberList.ContainsKey(characterId))
		{
			SelectedMemberList.Remove(characterId);
			if (SelectedNumText != null)
			{
				SelectedNumText.text = SelectedMemberList.Count().ToString();
			}
			return true;
		}
		return false;
	}

	public void OnDecide()
	{
		SingletonMonoBehaviour<MailSendManager>.Instance.CopyMemberList(SelectedMemberList);
		SingletonMonoBehaviour<NavigationViewController>.Instance.Pop();
	}
}
