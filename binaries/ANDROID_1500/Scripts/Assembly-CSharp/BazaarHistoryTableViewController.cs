using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class BazaarHistoryTableViewController : TableViewController<BazaarPriceHistory>
{
	[SerializeField]
	private Text EmptyText;

	public void LoadData(uint itemId)
	{
		Initialize();
		EmptyText.enabled = false;
		StartCoroutine(Bazaar.GetPriceHistory(delegate(BazaarPriceHistoryList res)
		{
			if (res.HistoryList.Count <= 0)
			{
				EmptyText.enabled = true;
			}
			foreach (BazaarPriceHistory history in res.HistoryList)
			{
				TableData.Add(history);
			}
			UpdateContents();
		}, null, itemId, CacheOption.OneMinute, LoadingAnimation.Default));
	}
}
