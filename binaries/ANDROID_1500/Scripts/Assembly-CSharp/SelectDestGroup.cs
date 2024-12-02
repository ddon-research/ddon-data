using UnityEngine;
using UnityEngine.UI;

public class SelectDestGroup : MonoBehaviour
{
	[SerializeField]
	private Toggle ToggleClan;

	[SerializeField]
	private Toggle ToggleFriend;

	[SerializeField]
	private ViewController ClanMemberView;

	[SerializeField]
	private ViewController FriendView;

	private void OnEnable()
	{
		if (SingletonMonoBehaviour<MailSendManager>.Instance.SelectedAddrCategory == MailSendManager.AddrCategory.ClanMember)
		{
			ToggleClan.isOn = true;
			ToggleFriend.isOn = false;
		}
		else
		{
			ToggleFriend.isOn = true;
			ToggleClan.isOn = false;
		}
	}

	public void ToMemberSelectPage(bool isForce)
	{
		if (ToggleClan.isOn)
		{
			if (SingletonMonoBehaviour<MailSendManager>.Instance.SetAddrCategory(MailSendManager.AddrCategory.ClanMember) || isForce)
			{
				ClanMemberView.Push();
			}
		}
		else if (SingletonMonoBehaviour<MailSendManager>.Instance.SetAddrCategory(MailSendManager.AddrCategory.Friend) || isForce)
		{
			FriendView.Push();
		}
	}
}
