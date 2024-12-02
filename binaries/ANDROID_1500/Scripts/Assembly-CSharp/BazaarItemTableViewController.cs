using System;
using Packet;
using WebRequest;

public class BazaarItemTableViewController : TableViewController<BazaarItem>
{
	public bool IsContents => TableData.Count > 0;

	public void LoadData(uint mainCategory, uint subCategory, uint rank, Action<uint, bool> onResult)
	{
		Initialize();
		StartCoroutine(Bazaar.GetItemList(delegate(BazaarItemList res)
		{
			onResult((uint)res.Items.Count, res.IsTooManyResult);
			foreach (BazaarItem item in res.Items)
			{
				TableData.Add(item);
			}
			UpdateContents();
		}, null, mainCategory, subCategory, rank, CacheOption.OneMinute, LoadingAnimation.Default));
	}
}
