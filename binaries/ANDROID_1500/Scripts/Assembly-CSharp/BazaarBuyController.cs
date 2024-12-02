using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.UI;

public class BazaarBuyController : ViewController
{
	[SerializeField]
	private ItemIcon ItemIcon;

	[SerializeField]
	private Text ItemText;

	[SerializeField]
	private Button ToItemDetailButton;

	[SerializeField]
	private GameObject BuyPage;

	[SerializeField]
	private GameObject HistoryPage;

	[SerializeField]
	private BazaarBuyTableViewController BuyTableView;

	[SerializeField]
	private BazaarHistoryTableViewController HistoryTableView;

	[SerializeField]
	private Toggle TabSelling;

	[SerializeField]
	private Toggle TabPriceHisotry;

	private uint ItemId;

	private string ItemName;

	private BazaarItem ItemData;

	[SerializeField]
	private BazaarSellController SellView;

	public void Setup(BazaarItem data)
	{
		ItemData = data;
	}

	private void OnEnable()
	{
		if (SingletonMonoBehaviour<NavigationViewController>.Instance.PrevNavigationDir != NavigationViewController.NavigationDir.Back)
		{
			BuyTableView.Clear();
			TabSelling.isOn = true;
			TabPriceHisotry.isOn = false;
			ItemText.text = ItemData.Item.Name;
			ItemIcon.Load(ItemData.Item.IconName, ItemData.Item.IconColorId);
			BuyPage.SetActive(value: true);
			HistoryPage.SetActive(value: false);
			BuyTableView.LoadData(ItemData.Item.ItemID);
		}
	}

	public void OnValueChangedBuy(bool b)
	{
		if (b && !BuyPage.activeSelf)
		{
			BuyPage.SetActive(value: true);
			HistoryPage.SetActive(value: false);
			BuyTableView.LoadData(ItemData.Item.ItemID);
		}
	}

	public void OnValueChangedHistory(bool b)
	{
		if (b && !HistoryPage.activeSelf)
		{
			HistoryPage.SetActive(value: true);
			BuyPage.SetActive(value: false);
			HistoryTableView.LoadData(ItemData.Item.ItemID);
		}
	}

	public void OnClickExhibit()
	{
		StartCoroutine(BazaarItemSearchController.ShowSellView(ItemData, delegate(List<StorageSlotItem> storageItems)
		{
			SellView.Initialize(ItemData.Item.ItemID, ItemData.Item.Name, ItemData.Item.IconName, ItemData.Item.IconColorId, storageItems);
			SellView.Push();
		}));
	}
}
