using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.UI;
using Utility;

public class CraftRefineItemTableViewCell : TableViewCell<ItemData>
{
	private Button ClickButton;

	[SerializeField]
	private Text Name;

	[SerializeField]
	private ItemIcon ItemIcon;

	private ItemData Data;

	[SerializeField]
	private ItemPicker ItemPicker;

	private void Start()
	{
		ClickButton = GetComponent<Button>();
		ClickButton.onClick.AddListener(OnClick);
	}

	public override void UpdateContent(ItemData itemData)
	{
		Data = itemData;
		Name.text = itemData.Name;
		ItemIcon.Load(itemData.IconName, itemData.IconColorId);
	}

	public void OnClick()
	{
		ItemPicker.Push();
		ItemPicker.Setup(Data.ItemID, Data.Name, 1u, delegate(List<StorageSlotItem> ret)
		{
			if (ret.Count != 0)
			{
				StorageSlotItem storageSlotItem = ret.Find((StorageSlotItem elem) => elem.Num != 0);
				if (storageSlotItem != null)
				{
					SingletonMonoBehaviour<CraftManager>.Instance.RefineItem = storageSlotItem;
					SingletonMonoBehaviour<CraftManager>.Instance.RefineItem.Item = Data;
				}
			}
		}, SingletonMonoBehaviour<CraftManager>.Instance.GetRefineItemNum, 2u);
	}
}
