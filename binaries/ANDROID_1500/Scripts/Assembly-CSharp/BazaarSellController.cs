using System;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class BazaarSellController : ViewController
{
	[SerializeField]
	private new ItemIcon Icon;

	[SerializeField]
	private Text ItemNameText;

	[SerializeField]
	private Text MinPrice;

	[SerializeField]
	private Text MaxPrice;

	[SerializeField]
	private InputField PriceInput;

	[SerializeField]
	private Text MaxNum;

	[SerializeField]
	private InputField NumInput;

	[SerializeField]
	private Text TotalGold;

	[SerializeField]
	private GameObject SettingPage;

	[SerializeField]
	private GameObject ExhibitListPage;

	[SerializeField]
	private GameObject HistoryPage;

	[SerializeField]
	private BazaarBuyTableViewController BuyTableView;

	[SerializeField]
	private BazaarHistoryTableViewController HistoryTableView;

	[SerializeField]
	private Toggle SettingTab;

	[SerializeField]
	private Toggle ExhibitListTab;

	[SerializeField]
	private Toggle HistoryTab;

	[SerializeField]
	private ViewController AcceptedView;

	private uint ItemId;

	private BazaarExhibitLimit Limit;

	private string IconName;

	private uint IconColorId;

	private List<StorageSlotItem> StorageItems;

	private ushort StorageItemNum;

	private void Start()
	{
		PriceInput.onEndEdit.AddListener(OnEndEditPrice);
		NumInput.onEndEdit.AddListener(OnEndEditNum);
	}

	private void OnEnable()
	{
		SettingPage.SetActive(value: true);
		ExhibitListPage.SetActive(value: false);
		HistoryPage.SetActive(value: false);
		SettingTab.isOn = true;
		ExhibitListTab.isOn = false;
		HistoryTab.isOn = false;
		Icon.Load(IconName, IconColorId);
		StartCoroutine(Bazaar.GetExhibitLimit(delegate(BazaarExhibitLimit res)
		{
			Limit = res;
			MinPrice.text = res.PriceMin.ToString("N0");
			MaxPrice.text = res.PriceMax.ToString("N0");
			MaxNum.text = Math.Min(res.NumMax, StorageItemNum).ToString();
			PriceInput.text = res.PriceMin.ToString();
			TotalGold.text = MinPrice.text.WithComma();
		}, null, ItemId, null, LoadingAnimation.Default));
	}

	public void OnClickSellDicide()
	{
		SingletonMonoBehaviour<UseJemDialog>.Instance.Show("アイテム出品", 1u, delegate(bool res)
		{
			if (res)
			{
				Exhibit();
			}
		});
	}

	private void Exhibit()
	{
		BazaarExhibitRequest bazaarExhibitRequest = new BazaarExhibitRequest();
		bazaarExhibitRequest.ItemId = ItemId;
		bazaarExhibitRequest.Price = uint.Parse(PriceInput.text);
		ushort num = ushort.Parse(NumInput.text);
		foreach (StorageSlotItem storageItem in StorageItems)
		{
			StorageSlotItem storageSlotItem = new StorageSlotItem();
			storageSlotItem.Address.Storage = storageItem.Address.Storage;
			storageSlotItem.Address.SlotNo = storageItem.Address.SlotNo;
			storageSlotItem.Item = storageItem.Item;
			if (storageItem.Num >= num)
			{
				storageSlotItem.Num = num;
				num = 0;
				bazaarExhibitRequest.ExhibitItems.Add(storageSlotItem);
				break;
			}
			storageSlotItem.Num = storageItem.Num;
			num -= (ushort)storageItem.Num;
			bazaarExhibitRequest.ExhibitItems.Add(storageSlotItem);
		}
		StartCoroutine(Bazaar.PostExhibitItem(delegate(JemResult result)
		{
			ItemStorage.ClearCache();
			Bazaar.ClearCache_GetExhibitListUInt32();
			SingletonMonoBehaviour<ChargeManager>.Instance.SetJem(result.JemList);
			AcceptedView.Push();
		}, null, bazaarExhibitRequest, LoadingAnimation.Default));
	}

	public void OnClickSellCancel()
	{
		SingletonMonoBehaviour<NavigationViewController>.Instance.Pop();
	}

	public void OnEndEditPrice(string text)
	{
		if (uint.TryParse(text, out var result))
		{
			if (result > Limit.PriceMax)
			{
				result = Limit.PriceMax;
			}
			if (result < Limit.PriceMin)
			{
				result = Limit.PriceMin;
			}
		}
		else
		{
			result = Limit.PriceMin;
		}
		PriceInput.text = result.ToString();
		ushort num = ushort.Parse(NumInput.text);
		TotalGold.text = (result * num).ToString("N0");
	}

	public void OnEndEditNum(string text)
	{
		ushort result = 0;
		ushort.TryParse(text, out result);
		if (result == 0)
		{
			result = 1;
		}
		if (result > Limit.NumMax)
		{
			result = Limit.NumMax;
		}
		if (result > StorageItemNum)
		{
			result = StorageItemNum;
		}
		NumInput.text = result.ToString();
		uint num = uint.Parse(PriceInput.text);
		TotalGold.text = (num * result).ToString("N0");
	}

	public ushort GetStorageItemNum()
	{
		ushort num = 0;
		foreach (StorageSlotItem storageItem in StorageItems)
		{
			num += (ushort)storageItem.Num;
		}
		return num;
	}

	public void Initialize(uint itemId, string itemName, string iconName, uint iconColorId, List<StorageSlotItem> storageItems)
	{
		ItemId = itemId;
		ItemNameText.text = itemName;
		PriceInput.text = "0";
		NumInput.text = "1";
		IconName = iconName;
		IconColorId = iconColorId;
		TotalGold.text = "0";
		StorageItems = storageItems;
		StorageItemNum = GetStorageItemNum();
	}

	public void OnValueChangedSetting(bool b)
	{
		if (b && !SettingPage.activeSelf)
		{
			SettingPage.SetActive(value: true);
			ExhibitListPage.SetActive(value: false);
			HistoryPage.SetActive(value: false);
		}
	}

	public void OnValueChangedHistory(bool b)
	{
		if (b && !HistoryPage.activeSelf)
		{
			HistoryPage.SetActive(value: true);
			ExhibitListPage.SetActive(value: false);
			SettingPage.SetActive(value: false);
			HistoryTableView.LoadData(ItemId);
		}
	}

	public void OnValueChangedExhibitList(bool b)
	{
		if (b && !ExhibitListPage.activeSelf)
		{
			ExhibitListPage.SetActive(value: true);
			HistoryPage.SetActive(value: false);
			SettingPage.SetActive(value: false);
			BuyTableView.LoadData(ItemId);
		}
	}
}
