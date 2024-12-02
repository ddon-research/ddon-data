using System.Collections.Generic;
using System.IO;
using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class MailSend : MonoBehaviour
{
	[SerializeField]
	private Image AddrGroup_NoSelect;

	[SerializeField]
	private Image AddrGroup_ClanMember;

	[SerializeField]
	private Image AddrGroup_Friend;

	[SerializeField]
	private ViewController GroupSelectView;

	[SerializeField]
	private ViewController ClanMemberSelectView;

	[SerializeField]
	private ViewController FriendSelectView;

	[SerializeField]
	private Text DefaultText;

	[SerializeField]
	private List<SendMemberListElement> SendMemberListElements;

	[SerializeField]
	private GameObject OtherSendMemberTextObject;

	[SerializeField]
	private Text OtherSendMemberNum;

	[SerializeField]
	private InputField MailTextInput;

	private void OnEnable()
	{
		AddrGroup_NoSelect.gameObject.SetActive(value: false);
		AddrGroup_ClanMember.gameObject.SetActive(value: false);
		AddrGroup_Friend.gameObject.SetActive(value: false);
		DefaultText.gameObject.SetActive(value: false);
		if (SingletonMonoBehaviour<MailSendManager>.Instance.SelectedMemberList.Count == 0)
		{
			AddrGroup_NoSelect.gameObject.SetActive(value: true);
			DefaultText.gameObject.SetActive(value: true);
		}
		else if (SingletonMonoBehaviour<MailSendManager>.Instance.SelectedAddrCategory == MailSendManager.AddrCategory.ClanMember)
		{
			AddrGroup_ClanMember.gameObject.SetActive(value: true);
		}
		else
		{
			AddrGroup_Friend.gameObject.SetActive(value: true);
		}
		foreach (SendMemberListElement sendMemberListElement in SendMemberListElements)
		{
			sendMemberListElement.gameObject.SetActive(value: false);
		}
		ShowMemberList();
	}

	private void ShowMemberList()
	{
		int num = 0;
		foreach (KeyValuePair<uint, MemberListData> selectedMember in SingletonMonoBehaviour<MailSendManager>.Instance.SelectedMemberList)
		{
			if (num >= SendMemberListElements.Count)
			{
				break;
			}
			SendMemberListElements[num].gameObject.SetActive(value: true);
			SendMemberListElements[num].UpdateContents(selectedMember.Value.CharIconId, selectedMember.Value.FirstName, selectedMember.Value.LastName);
			num++;
		}
		if (SingletonMonoBehaviour<MailSendManager>.Instance.SelectedMemberList.Count > SendMemberListElements.Count)
		{
			OtherSendMemberTextObject.SetActive(value: true);
			OtherSendMemberNum.text = (SingletonMonoBehaviour<MailSendManager>.Instance.SelectedMemberList.Count - SendMemberListElements.Count).ToString();
		}
		else
		{
			OtherSendMemberTextObject.SetActive(value: false);
		}
	}

	public void ClearMemberList()
	{
		SingletonMonoBehaviour<MailSendManager>.Instance.ClearMemberList();
	}

	public void ShowAddrSelect()
	{
		if (SingletonMonoBehaviour<MailSendManager>.Instance.SelectedMemberList.Count == 0)
		{
			GroupSelectView.Push();
		}
		else if (SingletonMonoBehaviour<MailSendManager>.Instance.SelectedAddrCategory == MailSendManager.AddrCategory.ClanMember)
		{
			ClanMemberSelectView.Push();
		}
		else
		{
			FriendSelectView.Push();
		}
	}

	public void Send()
	{
		if (SingletonMonoBehaviour<MailSendManager>.Instance.SelectedMemberList.Count == 0)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "宛先を選択してください");
			return;
		}
		SingletonMonoBehaviour<UseJemDialog>.Instance.Show("メール送信", 1u, delegate(bool res)
		{
			if (res)
			{
				SendRequest();
			}
		});
	}

	private void SendRequest()
	{
		MailSendData mailSendData = new MailSendData();
		foreach (KeyValuePair<uint, MemberListData> selectedMember in SingletonMonoBehaviour<MailSendManager>.Instance.SelectedMemberList)
		{
			mailSendData.ToCharacterIDs.Add(selectedMember.Value.CharacterId);
		}
		mailSendData.Text = MailTextInput.text;
		string empty = string.Empty;
		empty = ((mailSendData.Text.Length <= 20) ? mailSendData.Text : mailSendData.Text.Substring(0, 20));
		StringReader stringReader = new StringReader(empty);
		string text = stringReader.ReadLine();
		if (text != null)
		{
			mailSendData.Title = text;
		}
		else
		{
			mailSendData.Title = string.Empty;
		}
		StartCoroutine(Mail.Post(delegate(JemResult result)
		{
			SingletonMonoBehaviour<ChargeManager>.Instance.SetJem(result.JemList);
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "送信完了", delegate
			{
				MailTextInput.text = string.Empty;
				SingletonMonoBehaviour<MailSendManager>.Instance.SelectedMemberList.Clear();
				SingletonMonoBehaviour<NavigationViewController>.Instance.Pop();
			});
		}, null, mailSendData, LoadingAnimation.Default));
	}
}
