using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.UI;

public class InventoryItemPanel : ViewController
{
	[SerializeField]
	private new ItemIcon Icon;

	[SerializeField]
	private Text ItemName;

	[SerializeField]
	private Text ItemNum;

	[SerializeField]
	private GameObject NumArea;

	[SerializeField]
	private BazaarSellController BazaarSelView;

	private InventoryController.Mode ClickMode;

	private StorageType StorageType;

	private StorageItem StorageItem;

	private void Start()
	{
		GetComponent<Button>().onClick.AddListener(OnClick);
	}

	public void UpdateContent(InventoryController.Mode clickMode, StorageType storageType, StorageItem item)
	{
		ClickMode = clickMode;
		StorageType = storageType;
		StorageItem = item;
		ModeInit(clickMode, item);
		if (item.Num == 0)
		{
			NumArea.SetActive(value: false);
			Icon.gameObject.SetActive(value: false);
			ItemName.gameObject.SetActive(value: false);
			return;
		}
		NumArea.SetActive(value: true);
		ItemNum.text = item.Num.ToString();
		Icon.gameObject.SetActive(value: true);
		Icon.Load(item.Item.IconName, item.Item.IconColorId);
		ItemName.gameObject.SetActive(value: true);
		ItemName.text = item.Item.Name;
	}

	private void ModeInit(InventoryController.Mode mode, StorageItem item)
	{
		if (mode == InventoryController.Mode.BazaarExhibit && !item.Item.CanBazaar)
		{
			base.CachedCanvasGroup.interactable = false;
			base.CachedCanvasGroup.alpha = 0.5f;
		}
	}

	private void OnClick()
	{
		InventoryController.Mode clickMode = ClickMode;
		if (clickMode != 0 && clickMode == InventoryController.Mode.BazaarExhibit)
		{
			List<StorageSlotItem> list = new List<StorageSlotItem>();
			StorageSlotItem storageSlotItem = new StorageSlotItem();
			storageSlotItem.Address.Storage = StorageType;
			storageSlotItem.Address.SlotNo = StorageItem.SlotNo;
			storageSlotItem.Item.ItemID = StorageItem.Item.ItemID;
			storageSlotItem.Num = StorageItem.Num;
			list.Add(storageSlotItem);
			BazaarSelView.Initialize(StorageItem.Item.ItemID, StorageItem.Item.Name, StorageItem.Item.IconName, StorageItem.Item.IconColorId, list);
			BazaarSelView.Push();
		}
	}
}
