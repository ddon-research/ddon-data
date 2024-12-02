using UnityEngine;
using UnityEngine.UI;

public class MemberListTableViewElement : TableViewCell<MemberListData>
{
	public MemberListData DataSource;

	[SerializeField]
	private Toggle OnlineToggle;

	[SerializeField]
	private CharacterIconController CharacterIcon;

	[SerializeField]
	private Text FirstName;

	[SerializeField]
	private Text LastName;

	[SerializeField]
	private Image JobIcon;

	[SerializeField]
	private Text JobLv;

	[SerializeField]
	private GameObject IsFriendIcon;

	[SerializeField]
	private GameObject IsClanMemberIcon;

	[SerializeField]
	private Image ClanMasterIcon;

	[SerializeField]
	private Image ClanLeaderIcon;

	public override void UpdateContent(MemberListData data)
	{
		CharacterIcon.LoadImageAsync(data.CharIconId);
		FirstName.text = data.FirstName;
		LastName.text = data.LastName;
		JobIcon.sprite = SingletonMonoBehaviour<SpriteManager>.Instance.GetJobIcon(data.JobId);
		JobLv.text = data.JobLv.ToString();
		IsFriendIcon.SetActive(data.IsFriend);
		OnlineToggle.isOn = data.IsOnline;
		if (data.IsClanMember)
		{
			IsClanMemberIcon.SetActive(data.ClanMemberRank >= 2);
			if (ClanMasterIcon != null)
			{
				ClanMasterIcon.gameObject.SetActive(data.ClanMemberRank == 1);
			}
			if (ClanLeaderIcon != null)
			{
				ClanLeaderIcon.gameObject.SetActive(data.ClanMemberRank == 2);
			}
		}
		else
		{
			IsClanMemberIcon.SetActive(value: false);
			if (ClanMasterIcon != null)
			{
				ClanMasterIcon.gameObject.SetActive(value: false);
			}
			if (ClanLeaderIcon != null)
			{
				ClanLeaderIcon.gameObject.SetActive(value: false);
			}
		}
		DataSource = data;
	}

	public void OpenMemberProfile()
	{
		SingletonMonoBehaviour<ProfileManager>.Instance.OpenProfilePlayer(DataSource.CharacterId);
	}
}
