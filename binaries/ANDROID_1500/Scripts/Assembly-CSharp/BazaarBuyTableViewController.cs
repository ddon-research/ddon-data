using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class BazaarBuyTableViewController : TableViewController<BazaarExhibitElement>
{
	[SerializeField]
	private Text EmptyText;

	private bool isLoading;

	public void LoadData(uint itemId)
	{
		if (isLoading)
		{
			return;
		}
		isLoading = true;
		Initialize();
		EmptyText.enabled = false;
		StartCoroutine(Bazaar.GetExhibitList(delegate(BazaarExhibitElementList res)
		{
			if (res.Items.Count <= 0)
			{
				EmptyText.enabled = true;
			}
			foreach (BazaarExhibitElement item in res.Items)
			{
				TableData.Add(item);
			}
			UpdateContents();
			isLoading = false;
		}, delegate
		{
			isLoading = false;
		}, itemId, CacheOption.ThreeSecond, LoadingAnimation.Default));
	}

	public void Clear()
	{
		isLoading = false;
	}
}
