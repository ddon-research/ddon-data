using System;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class Mail_Detail : ViewController
{
	private GameObject Dialog;

	private MailDatailData Data;

	[SerializeField]
	private Text SenderFirstName;

	[SerializeField]
	private Text SenderLastName;

	[SerializeField]
	private Text ReceivedAt;

	[SerializeField]
	private Text TitleLabel;

	[SerializeField]
	private Image OpenIcon;

	[SerializeField]
	private Image CloseIcon;

	[SerializeField]
	private CharacterIconController CharacterIcon;

	[SerializeField]
	private Text BodyText;

	[SerializeField]
	private Mail_ListBoxController ItemController;

	public ulong ID { get; set; }

	private void OnEnable()
	{
		LoadData();
	}

	private void OnDisable()
	{
	}

	private void LoadData()
	{
		SenderFirstName.text = string.Empty;
		SenderLastName.text = string.Empty;
		ReceivedAt.text = string.Empty;
		BodyText.text = string.Empty;
		if (ItemController != null)
		{
			ItemController.Clear();
		}
		if (CharacterIcon != null)
		{
			CharacterIcon.gameObject.SetActive(value: false);
		}
		StartCoroutine(Mail.GetReceivedDetail(delegate(MailReceivedDetail ret)
		{
			if (ret == null)
			{
				SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "エラー", "<color=#d94d4d>メール取得時にエラーが発生しました。</color>", delegate(ModalDialog.Result res)
				{
					if (res == ModalDialog.Result.OK)
					{
						SingletonMonoBehaviour<NavigationViewController>.Instance.Pop();
					}
				});
			}
			else
			{
				Data = new MailDatailData
				{
					Status = ((ret.Text.State == 1) ? MailListData.ReadStatus.Read : MailListData.ReadStatus.Unread),
					ReceivedAt = GameDateTimeConverter.FromUnixTime(ret.Text.Created),
					Title = ret.Text.Name,
					Body = ret.Text.Text
				};
				if (ret.Text.SenderCharacterId == 0)
				{
					Data.SenderFirstName = ret.Text.Name;
				}
				else
				{
					Data.SenderFirstName = ret.Text.SenderCharacterFirstName;
					Data.SenderLastName = ret.Text.SenderCharacterLastName;
					Data.CharacterIconID = ret.Text.SenderCharacterIconId;
				}
				Data.ItemReceived = ret.Text.ItemReceived;
				Data.Items = new List<MailItem>(ret.Items);
				Data.Gps = ret.Gps.Count;
				Data.GpCourses = ret.GpCourses.Count;
				UpdateContent(Data);
			}
		}, null, ID, CacheOption.OneMinute));
	}

	private void ShowDialog()
	{
		List<ButtomDialogData> list = new List<ButtomDialogData>();
		list.Add(new ButtomDialogData
		{
			Name = "閉じる",
			OnClick = OnClickDialog_Close
		});
		list.Add(new ButtomDialogData
		{
			Name = "返信",
			OnClick = OnClickDialog_Reply
		});
		List<ButtomDialogData> datas = list;
		Dialog = ButtomDialogController.CreateDialog(base.gameObject.transform.parent, datas);
	}

	private void OnClickDialog_Close()
	{
	}

	private void OnClickDialog_Reply()
	{
	}

	public override void OnNavigationPushEnd()
	{
	}

	public override void OnNavigationPopBegin()
	{
	}

	private void UpdateContent(MailDatailData itemData)
	{
		SenderFirstName.text = itemData.SenderFirstName;
		SenderLastName.text = itemData.SenderLastName;
		ReceivedAt.text = itemData.ReceivedAt.ToString("yyyy/MM/dd (ddd) HH:mm");
		if (itemData.Status == MailListData.ReadStatus.Read)
		{
			OpenIcon.gameObject.SetActive(value: true);
			CloseIcon.gameObject.SetActive(value: false);
		}
		else
		{
			OpenIcon.gameObject.SetActive(value: false);
			CloseIcon.gameObject.SetActive(value: true);
		}
		if (CharacterIcon != null)
		{
			CharacterIcon.gameObject.SetActive(value: true);
			CharacterIcon.LoadImageAsync(itemData.CharacterIconID);
		}
		BodyText.text = itemData.Body;
		for (int i = 0; i < 5; i++)
		{
			BodyText.text += System.Environment.NewLine;
		}
		if (!(ItemController != null))
		{
			return;
		}
		List<Mail_ListBoxData> list = new List<Mail_ListBoxData>();
		int num = 1;
		foreach (MailItem item in itemData.Items)
		{
			Mail_ListBoxData mail_ListBoxData = new Mail_ListBoxData();
			mail_ListBoxData.Name = item.ItemName;
			mail_ListBoxData.IsReceived = (itemData.ItemReceived & (1 << num)) == 0;
			list.Add(mail_ListBoxData);
			num++;
		}
		for (int j = 0; j < itemData.Gps; j++)
		{
			Mail_ListBoxData mail_ListBoxData2 = new Mail_ListBoxData();
			mail_ListBoxData2.Name = "黄金石";
			mail_ListBoxData2.IsReceived = (itemData.ItemReceived & (1 << num)) == 0;
			list.Add(mail_ListBoxData2);
			num++;
		}
		for (int k = 0; k < itemData.GpCourses; k++)
		{
			Mail_ListBoxData mail_ListBoxData3 = new Mail_ListBoxData();
			mail_ListBoxData3.Name = "パスポート・コース";
			mail_ListBoxData3.IsReceived = (itemData.ItemReceived & (1 << num)) == 0;
			list.Add(mail_ListBoxData3);
			num++;
		}
		ItemController.DataSources = list;
		ItemController.CreateElements();
	}
}
