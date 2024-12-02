using System;
using System.Collections;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using WebRequest;

namespace Utility;

public class ItemPickerStorageListBox : ViewController
{
	[SerializeField]
	private List<ItemPickerStorageData> DataSource = new List<ItemPickerStorageData>();

	[SerializeField]
	private ItemPickerStorageElement StorageElement;

	public IEnumerator Load(StorageType storageType, uint itemId, Func<StorageType, ushort, uint> onLoadSelectedItem)
	{
		yield return ItemStorage.GetItemFromStorageForWrite(delegate(CharacterItemStorage res)
		{
			SetStorage(storageType, res, onLoadSelectedItem);
		}, null, storageType, itemId, CacheOption.OneMinute);
	}

	public void SetStorage(StorageType storageType, CharacterItemStorage storage, Func<StorageType, ushort, uint> onLoadSelectedItem)
	{
		DataSource.Clear();
		base.CachedCanvasGroup.interactable = storage.IsAvailable;
		foreach (StorageItem item in storage.ItemList)
		{
			ItemPickerStorageData itemPickerStorageData = new ItemPickerStorageData();
			itemPickerStorageData.StorageTyep = storageType;
			itemPickerStorageData.SlotNo = item.SlotNo;
			itemPickerStorageData.MaxNum = item.Num;
			itemPickerStorageData.ItemId = item.Item.ItemID;
			itemPickerStorageData.SelectedNum = onLoadSelectedItem(storageType, item.SlotNo);
			DataSource.Add(itemPickerStorageData);
		}
		if (storage.ItemList.Count == 0)
		{
			base.CachedCanvasGroup.alpha = 0.8f;
			base.CachedCanvasGroup.interactable = false;
		}
		else
		{
			base.CachedCanvasGroup.alpha = 1f;
			base.CachedCanvasGroup.interactable = true;
		}
		StorageElement.UpdateContent(DataSource);
	}

	public void AppendSelectedItemList(List<StorageSlotItem> list)
	{
		foreach (ItemPickerStorageData item in DataSource)
		{
			StorageSlotItem storageSlotItem = new StorageSlotItem();
			storageSlotItem.Address.Storage = item.StorageTyep;
			storageSlotItem.Address.SlotNo = item.SlotNo;
			storageSlotItem.Num = item.SelectedNum;
			storageSlotItem.Item.ItemID = item.ItemId;
			list.Add(storageSlotItem);
		}
	}

	public void Clear()
	{
		base.CachedCanvasGroup.alpha = 0.8f;
		base.CachedCanvasGroup.interactable = false;
		DataSource.Clear();
		StorageElement.Clear();
	}
}
