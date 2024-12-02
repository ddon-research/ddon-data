using Packet;
using UnityEngine;
using UnityEngine.UI;

public class BazaarHistoryTableViewCell : TableViewCell<BazaarPriceHistory>
{
	[SerializeField]
	private Text Date;

	[SerializeField]
	private Text UnitPrice;

	[SerializeField]
	private Text Num;

	[SerializeField]
	private Text TotalPrice;

	public BazaarPriceHistory Data;

	public override void UpdateContent(BazaarPriceHistory itemData)
	{
		Data = itemData;
		Date.text = GameDateTimeConverter.FromUnixTime(itemData.Created).ToString("yyyy/MM/dd");
		UnitPrice.text = itemData.Price.ToString("N0");
		Num.text = itemData.Num.ToString();
		TotalPrice.text = (itemData.Price * itemData.Num).ToString("N0");
	}
}
