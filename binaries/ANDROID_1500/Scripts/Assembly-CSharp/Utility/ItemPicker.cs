using System;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

namespace Utility;

public class ItemPicker : ViewController
{
	[SerializeField]
	private Text ItemNameText;

	[SerializeField]
	private Text NeedNumText;

	[SerializeField]
	private ItemPickerStorageListBox ItemBagUseList;

	[SerializeField]
	private ItemPickerStorageListBox ItemBagMaterialList;

	[SerializeField]
	private ItemPickerStorageListBox WarehouseList;

	[SerializeField]
	private ItemPickerStorageListBox WarehouseExList;

	[SerializeField]
	private ItemPickerStorageListBox Baggage1List;

	[SerializeField]
	private ItemPickerStorageListBox Baggage2List;

	[SerializeField]
	private ItemPickerStorageListBox Baggage3List;

	[SerializeField]
	private Text ResultNeedNumText;

	[SerializeField]
	private Text ResultSelectedNumText;

	private uint ItemID;

	private uint NeedNum;

	private uint SelectedNum;

	[SerializeField]
	private Color TooManyColor;

	[SerializeField]
	private Color EqualColor;

	[SerializeField]
	private Color TooLittleColor;

	private Action<List<StorageSlotItem>> OnPick;

	private Func<StorageType, ushort, uint> OnLoadSelectedItem;

	public uint GetNeedNum()
	{
		return NeedNum;
	}

	public void Setup(uint itemId, string itemName, uint needNum, Action<List<StorageSlotItem>> onPick, Func<StorageType, ushort, uint> onLoadSelectedItem, uint popCount = 1u)
	{
		ItemID = itemId;
		NeedNum = needNum;
		NeedNumText.text = NeedNum.ToString();
		ItemNameText.text = itemName;
		ResultSelectedNumText.text = 0.ToString();
		ResultNeedNumText.text = NeedNumText.text;
		ItemBagUseList.Clear();
		ItemBagMaterialList.Clear();
		WarehouseList.Clear();
		WarehouseExList.Clear();
		Baggage1List.Clear();
		Baggage2List.Clear();
		Baggage3List.Clear();
		OnPick = onPick;
		OnLoadSelectedItem = onLoadSelectedItem;
		PopCount = popCount;
		Load();
	}

	public void OnClickDecide()
	{
		List<StorageSlotItem> selectedItemAddrList = GetSelectedItemAddrList();
		if (SelectedNum > NeedNum)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "選択個数が多すぎます");
			return;
		}
		OnPick(selectedItemAddrList);
		for (uint num = 0u; num < PopCount; num++)
		{
			bool cantActive = true;
			if (num == PopCount - 1)
			{
				cantActive = false;
			}
			SingletonMonoBehaviour<NavigationViewController>.Instance.Pop(cantActive);
		}
	}

	public void UpdateSelectedNum()
	{
		List<StorageSlotItem> selectedItemAddrList = GetSelectedItemAddrList();
		uint num = 0u;
		foreach (StorageSlotItem item in selectedItemAddrList)
		{
			num += item.Num;
		}
		SelectedNum = num;
		ResultSelectedNumText.text = SelectedNum.ToString();
		if (SelectedNum > NeedNum)
		{
			ResultSelectedNumText.color = TooManyColor;
		}
		else if (SelectedNum < NeedNum)
		{
			ResultSelectedNumText.color = TooLittleColor;
		}
		else
		{
			ResultSelectedNumText.color = EqualColor;
		}
	}

	private List<StorageSlotItem> GetSelectedItemAddrList()
	{
		List<StorageSlotItem> list = new List<StorageSlotItem>();
		ItemBagUseList.AppendSelectedItemList(list);
		ItemBagMaterialList.AppendSelectedItemList(list);
		WarehouseList.AppendSelectedItemList(list);
		WarehouseExList.AppendSelectedItemList(list);
		Baggage1List.AppendSelectedItemList(list);
		Baggage2List.AppendSelectedItemList(list);
		Baggage3List.AppendSelectedItemList(list);
		return list;
	}

	private void Load()
	{
		StartCoroutine(ItemStorage.GetItemFromAllAvailableStorageForCraft(delegate(CharacterItemStorageList res)
		{
			foreach (CharacterItemStorage storage in res.StorageList)
			{
				switch (storage.StorageType)
				{
				case StorageType.TOP:
					ItemBagUseList.SetStorage(StorageType.TOP, storage, OnLoadSelectedItem);
					break;
				case StorageType.BAG_MATERIAL:
					ItemBagMaterialList.SetStorage(StorageType.BAG_MATERIAL, storage, OnLoadSelectedItem);
					break;
				case StorageType.STORAGE_ALL:
					WarehouseList.SetStorage(StorageType.STORAGE_ALL, storage, OnLoadSelectedItem);
					break;
				case StorageType.STORAGE_EX1_ALL:
					WarehouseExList.SetStorage(StorageType.STORAGE_EX1_ALL, storage, OnLoadSelectedItem);
					break;
				case StorageType.BAGGAGE_RENTAL01:
					Baggage1List.SetStorage(StorageType.BAGGAGE_RENTAL01, storage, OnLoadSelectedItem);
					break;
				case StorageType.BAGGAGE_RENTAL02:
					Baggage2List.SetStorage(StorageType.BAGGAGE_RENTAL02, storage, OnLoadSelectedItem);
					break;
				case StorageType.BAGGAGE_RENTAL03:
					Baggage3List.SetStorage(StorageType.BAGGAGE_RENTAL03, storage, OnLoadSelectedItem);
					break;
				}
			}
			UpdateSelectedNum();
		}, null, ItemID, CacheOption.OneMinute, LoadingAnimation.Default));
	}
}
