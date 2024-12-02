using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Utility;

public class ItemPickerStorageElement : MonoBehaviour
{
	[SerializeField]
	private InputField SelectedNumInput;

	[SerializeField]
	private Text MaxNumText;

	[SerializeField]
	private ItemPicker Picker;

	private List<ItemPickerStorageData> SlotItemList;

	private bool IsInitializing;

	private uint MaxNum;

	private void Awake()
	{
		SelectedNumInput.onEndEdit.AddListener(OnEndEditNum);
	}

	private void OnEnable()
	{
		IsInitializing = true;
		MaxNumText.text = string.Empty;
	}

	public void OnEndEditNum(string text)
	{
		if (uint.TryParse(text, out var result))
		{
			if (result > MaxNum)
			{
				result = MaxNum;
			}
			if (result > Picker.GetNeedNum())
			{
				result = Picker.GetNeedNum();
			}
		}
		else
		{
			result = 0u;
		}
		SelectedNumInput.text = result.ToString();
		foreach (ItemPickerStorageData slotItem in SlotItemList)
		{
			slotItem.SelectedNum = 0u;
		}
		foreach (ItemPickerStorageData slotItem2 in SlotItemList)
		{
			if (result <= slotItem2.MaxNum)
			{
				slotItem2.SelectedNum = result;
				break;
			}
			slotItem2.SelectedNum = slotItem2.MaxNum;
			result -= slotItem2.MaxNum;
		}
		Picker.UpdateSelectedNum();
	}

	public void UpdateContent(List<ItemPickerStorageData> itemDataList)
	{
		IsInitializing = true;
		SlotItemList = itemDataList;
		MaxNum = 0u;
		foreach (ItemPickerStorageData itemData in itemDataList)
		{
			MaxNum += itemData.MaxNum;
		}
		MaxNumText.text = MaxNum.ToString();
		uint num = 0u;
		foreach (ItemPickerStorageData slotItem in SlotItemList)
		{
			num += slotItem.SelectedNum;
		}
		SelectedNumInput.text = num.ToString();
		IsInitializing = false;
	}

	public void Clear()
	{
		SelectedNumInput.text = string.Empty;
		MaxNumText.text = string.Empty;
	}
}
