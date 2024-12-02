using UnityEngine;
using UnityEngine.UI;

public class SendMemberSelecter : MemberListTableViewElement
{
	[SerializeField]
	private Toggle SelectedToggle;

	[SerializeField]
	private MemberListTableViewController MemberListTableView;

	public void ToggleMember(Toggle toggle)
	{
		if (toggle.isOn)
		{
			MemberListTableView.AddMember(DataSource);
		}
		else
		{
			MemberListTableView.RemoveMember(DataSource.CharacterId);
		}
	}

	public override void UpdateContent(MemberListData data)
	{
		base.UpdateContent(data);
		if (data.IsMine)
		{
			SelectedToggle.gameObject.SetActive(value: false);
		}
		else
		{
			SelectedToggle.gameObject.SetActive(value: true);
		}
		SelectedToggle.isOn = SingletonMonoBehaviour<MailSendManager>.Instance.IsSelectedMember(DataSource.CharacterId);
	}
}
