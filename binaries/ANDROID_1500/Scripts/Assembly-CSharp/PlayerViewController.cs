using System.Collections;
using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class PlayerViewController : ViewControllerAfterLoad
{
	[SerializeField]
	private Text PlayerName;

	[SerializeField]
	private CharacterIconController PlayerIcon;

	[SerializeField]
	private Text PlayerJobName;

	[SerializeField]
	private Image PlayerJobIcon;

	[SerializeField]
	private Text PlayerJobLevel;

	[SerializeField]
	private Image PlayerSex;

	[SerializeField]
	private Text PlayerItemLevel;

	[SerializeField]
	private Text ProfileJobName;

	[SerializeField]
	private Text ProfileTitle;

	[SerializeField]
	private Text ProfileAdven;

	[SerializeField]
	private Text ProfileStyle;

	[SerializeField]
	private Text ProfileParty;

	[SerializeField]
	private Text[] ProfileJobIcon;

	[SerializeField]
	private Text ProfileComment;

	[SerializeField]
	private ClanEmblem ProfileClanIcon;

	[SerializeField]
	private Text ProfileClanName;

	[SerializeField]
	private Text ProfileClanLevel;

	[SerializeField]
	private Text ProfileClanMember;

	public uint CharacterId { get; set; }

	private void Initialize()
	{
		PlayerName.text = string.Empty;
		PlayerIcon.LoadImageAsync(0u);
		PlayerJobName.text = string.Empty;
		PlayerJobIcon.sprite = SingletonMonoBehaviour<SpriteManager>.Instance.GetJobIcon(0u);
		PlayerJobLevel.text = "1";
		PlayerSex.sprite = SingletonMonoBehaviour<ProfileManager>.Instance.GetSexIcon(0u);
		PlayerItemLevel.text = string.Empty;
		ProfileTitle.text = string.Empty;
		ProfileJobName.text = string.Empty;
		ProfileAdven.text = string.Empty;
		ProfileStyle.text = string.Empty;
		ProfileParty.text = string.Empty;
		for (int i = 0; i < ProfileJobIcon.Length; i++)
		{
			ProfileJobIcon[i].text = "1";
		}
		ProfileComment.text = string.Empty;
		ProfileClanIcon.SetEmblemEmpry();
		ProfileClanName.text = string.Empty;
		ProfileClanLevel.text = string.Empty;
		ProfileClanMember.text = string.Empty;
		PageScrollVeiw componentInChildren = GetComponentInChildren<PageScrollVeiw>();
		if (componentInChildren != null)
		{
			componentInChildren.ResetPage();
		}
	}

	protected override IEnumerator LoadRoutine(ReqestResult result)
	{
		Initialize();
		yield return StartCoroutine(CharacterData.GetCharacterProfile(delegate(PlayerProfile res)
		{
			PlayerName.text = res.Profile.FirstName + "\n" + res.Profile.LastName;
			PlayerIcon.LoadImageAsync(res.Profile.IconID);
			PlayerJobName.text = res.JobName;
			PlayerJobIcon.sprite = SingletonMonoBehaviour<SpriteManager>.Instance.GetJobIcon(res.JobID);
			ushort jobLevel = 1;
			foreach (JobLvData item in res.JobInfo)
			{
				if (item.JobId == res.JobID)
				{
					jobLevel = item.JobLv;
				}
				ProfileJobIcon[item.JobId - 1].text = item.JobLv.ToString();
			}
			PlayerJobLevel.text = jobLevel.ToString();
			PlayerSex.sprite = SingletonMonoBehaviour<ProfileManager>.Instance.GetSexIcon(res.Profile.Sex);
			PlayerItemLevel.text = res.ItemRank.ToString();
			ProfileTitle.text = ((!(res.Profile.Title == string.Empty)) ? res.Profile.Title : "称号なし");
			ProfileJobName.text = res.Profile.EntryJob;
			ProfileAdven.text = SingletonMonoBehaviour<ProfileManager>.Instance.GetPlayPurposName(res.Profile.Adven);
			ProfileStyle.text = SingletonMonoBehaviour<ProfileManager>.Instance.GetPlayStyleName(res.Profile.Style);
			ProfileParty.text = ((res.Profile.Party != 1) ? "許可しない" : "許可する");
			ProfileComment.text = res.Profile.Comment;
			ProfileClanName.text = res.Clan.Name;
			ProfileClanLevel.text = res.Clan.Lv.ToString();
			ProfileClanMember.text = res.Clan.ClanMember.ToString();
			if (res.Clan.ClanMember > 0)
			{
				ProfileClanIcon.SetEmblem(res.ClanEmblem.MarkType, res.ClanEmblem.BaseType, res.ClanEmblem.BaseMainColor, res.ClanEmblem.BaseSubColor);
			}
			SingletonMonoBehaviour<ProfileManager>.Instance.SetStatusBase(res.Profile.FirstName + " " + res.Profile.LastName, res.JobID, jobLevel, res.ItemRank);
		}, delegate
		{
			result.isError = true;
		}, CharacterId, CacheOption.OneMinute, LoadingAnimation.Default));
	}
}
