using System;
using Packet;
using UnityEngine;
using UnityEngine.UI;

public class PresentBoxTableViewCell : TableViewCell<CharacterGift>
{
	[SerializeField]
	private PresentBoxTableViewController Parent;

	[SerializeField]
	private Text ItemNameText;

	[SerializeField]
	private Text PresentText;

	[SerializeField]
	private Image IconImage;

	[SerializeField]
	private Text LimitText;

	private CharacterGift Data;

	public CharacterGift GetData()
	{
		return Data;
	}

	public override void UpdateContent(CharacterGift itemData)
	{
		Data = itemData;
		long num = 0L;
		foreach (CharacterGiftJem jem in Data.Jems)
		{
			num += jem.Value;
		}
		ItemNameText.text = "黄金石のカケラ ×" + num.ToString("N0");
		PresentText.text = Data.Text;
		if (Data.Expire == 0)
		{
			LimitText.text = "無期限";
			return;
		}
		DateTime dateTime = new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc).AddSeconds(Data.Expire).ToLocalTime();
		TimeSpan timeSpan = dateTime - DateTime.Now;
		if (timeSpan.Days <= 0)
		{
			LimitText.text = "あと" + timeSpan.Hours + "時間";
			return;
		}
		int days = timeSpan.Days;
		if (days > 999)
		{
			days = 999;
		}
		LimitText.text = "あと" + timeSpan.Days + "日";
	}

	public void RecleveGift()
	{
		if (Parent != null && Data.Id != 0)
		{
			Parent.ReceiveGift(Data.Id);
		}
	}
}
