using System;
using Packet;
using UnityEngine;
using UnityEngine.UI;

public class BazaarExhibitStatusTableViewCell : TableViewCell<BazaarExhibitingElement>
{
	[SerializeField]
	private GameObject ExhibitingPanel;

	[SerializeField]
	private GameObject ProceedsPanel;

	[SerializeField]
	private GameObject NonePanel;

	[SerializeField]
	private GameObject LockPanel;

	[SerializeField]
	private Text RemainTimeText;

	[SerializeField]
	private new ItemIcon Icon;

	[SerializeField]
	private Text ItemNameText;

	[SerializeField]
	private Text NumText;

	[SerializeField]
	private Text UnitPriceText;

	[SerializeField]
	private Text TotalPriceText;

	[SerializeField]
	private Text Proceeds_TotalPriceText;

	[SerializeField]
	private Text LockRemainTimeText;

	[SerializeField]
	private BazaarExhibitStatusController Controller;

	private BazaarExhibitingElement Data;

	public void Interrupt()
	{
		SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK_Cancel, "確認", ItemNameText.text + "の出品をキャンセルします\nよろしいですか？", delegate(ModalDialog.Result res)
		{
			if (res == ModalDialog.Result.OK)
			{
				Controller.InterruptExhibit(Data.ID);
			}
		});
	}

	public override void UpdateContent(BazaarExhibitingElement itemData)
	{
		Data = itemData;
		if (itemData.Status == E_BAZAAR_STATE.BAZAAR_STATE_EXHIBITING)
		{
			ExhibitingPanel.SetActive(value: true);
			ProceedsPanel.SetActive(value: false);
			NonePanel.SetActive(value: false);
			LockPanel.SetActive(value: false);
			TimeSpan timeSpan = TimeSpan.FromSeconds(itemData.RemainTime);
			RemainTimeText.text = ((int)timeSpan.TotalHours).ToString("D2") + ":" + timeSpan.Minutes.ToString("D2");
			if (timeSpan.TotalSeconds == 0.0)
			{
				RemainTimeText.text = "<color=#d94d4d>" + ((int)timeSpan.TotalHours).ToString("D2") + ":" + timeSpan.Minutes.ToString("D2") + "</color>";
			}
			Icon.Load(itemData.Item.IconName, itemData.Item.IconColorId);
			ItemNameText.text = itemData.Item.Name;
			NumText.text = itemData.Num.ToString();
			UnitPriceText.text = itemData.UnitPrice.ToString("N0");
			TotalPriceText.text = (itemData.Num * itemData.UnitPrice).ToString("N0");
		}
		else if (itemData.Status == E_BAZAAR_STATE.BAZAAR_STATE_PROCEEDS)
		{
			ExhibitingPanel.SetActive(value: false);
			ProceedsPanel.SetActive(value: true);
			NonePanel.SetActive(value: false);
			LockPanel.SetActive(value: false);
			Proceeds_TotalPriceText.text = itemData.Proceeds.ToString("N0");
		}
		else
		{
			ExhibitingPanel.SetActive(value: false);
			ProceedsPanel.SetActive(value: false);
			if (itemData.RemainTime > 0)
			{
				NonePanel.SetActive(value: false);
				LockPanel.SetActive(value: true);
				TimeSpan timeSpan2 = TimeSpan.FromSeconds(itemData.RemainTime);
				LockRemainTimeText.text = (int)timeSpan2.TotalHours + ":" + timeSpan2.Minutes;
			}
			else
			{
				NonePanel.SetActive(value: true);
				LockPanel.SetActive(value: false);
			}
		}
	}
}
