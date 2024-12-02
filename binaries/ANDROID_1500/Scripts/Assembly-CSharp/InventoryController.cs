using System;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class InventoryController : ViewController
{
	public enum StorageGroupType
	{
		Bag,
		Warehouse,
		Baggage,
		Post
	}

	public enum DataSourceType
	{
		BagUse,
		BagMaterial,
		BagEquip,
		BagJob,
		WerehouseFree,
		WerehouseEx,
		BaggageEx1,
		BaggageEx2,
		BaggageEx3,
		Post
	}

	public enum Mode
	{
		View,
		BazaarExhibit
	}

	public class DDOptionData : Dropdown.OptionData
	{
	}

	[SerializeField]
	private Sprite IconBag;

	[SerializeField]
	private Sprite IconWarehouse;

	[SerializeField]
	private Sprite IconBaggage;

	[SerializeField]
	private Sprite IconPost;

	[SerializeField]
	private GameObject TabArea;

	[SerializeField]
	private Toggle GroupTabBase;

	[SerializeField]
	private Text MaxNumText;

	[SerializeField]
	private Dropdown NumDD;

	[SerializeField]
	private InventoryItemPanel ItemPanelBase;

	private List<InventoryItemPanel> Panels = new List<InventoryItemPanel>();

	private List<Toggle> Tabs = new List<Toggle>();

	[SerializeField]
	private ScrollRect ItemScrollRect;

	[SerializeField]
	private Text EmptyText;

	private const uint LoadNumAtOnce = 40u;

	private StorageGroupType StorageGroup;

	private Mode CurrentMode;

	private DataSourceType SelectedDtataSourceType;

	private uint MaxSlotNum;

	private bool IsInitializingDD;

	private uint SlotMin;

	private uint SlotMax;

	public override Sprite Icon
	{
		get
		{
			if (StorageGroup == StorageGroupType.Bag)
			{
				return IconBag;
			}
			if (StorageGroup == StorageGroupType.Warehouse)
			{
				return IconWarehouse;
			}
			if (StorageGroup == StorageGroupType.Baggage)
			{
				return IconBaggage;
			}
			if (StorageGroup == StorageGroupType.Post)
			{
				return IconPost;
			}
			return IconBag;
		}
	}

	public override string Title
	{
		get
		{
			if (StorageGroup == StorageGroupType.Bag)
			{
				return "アイテムバッグ";
			}
			if (StorageGroup == StorageGroupType.Warehouse)
			{
				return "保管ボックス";
			}
			if (StorageGroup == StorageGroupType.Baggage)
			{
				return "格納チェスト";
			}
			if (StorageGroup == StorageGroupType.Post)
			{
				return "アイテムポスト";
			}
			return "アイテムバッグ";
		}
	}

	private void Start()
	{
		GroupTabBase.gameObject.SetActive(value: false);
		ItemPanelBase.gameObject.SetActive(value: false);
		NumDD.onValueChanged.AddListener(NumDD_OnValueChanged);
	}

	public void PushBag()
	{
		CurrentMode = Mode.View;
		StorageGroup = StorageGroupType.Bag;
		Push();
	}

	public void PushWarehouse()
	{
		CurrentMode = Mode.View;
		StorageGroup = StorageGroupType.Warehouse;
		Push();
	}

	public void PushBaggage()
	{
		CurrentMode = Mode.View;
		StorageGroup = StorageGroupType.Baggage;
		Push();
	}

	public void PushPost()
	{
		CurrentMode = Mode.View;
		StorageGroup = StorageGroupType.Post;
		Push();
	}

	public void PushBazaarExhibitBag()
	{
		CurrentMode = Mode.BazaarExhibit;
		StorageGroup = StorageGroupType.Bag;
		Push();
	}

	public void PushBazaarExhibitWarehouse()
	{
		CurrentMode = Mode.BazaarExhibit;
		StorageGroup = StorageGroupType.Warehouse;
		Push();
	}

	private void ClearTab()
	{
		foreach (Toggle tab in Tabs)
		{
			UnityEngine.Object.Destroy(tab.gameObject);
		}
		Tabs.Clear();
		EmptyText.enabled = true;
	}

	private void ClearPanel()
	{
		foreach (InventoryItemPanel panel in Panels)
		{
			UnityEngine.Object.Destroy(panel.gameObject);
		}
		Panels.Clear();
	}

	private void OnEnable()
	{
		ClearTab();
		ClearPanel();
		NumDD.options.Clear();
		NumDD.RefreshShownValue();
		MaxNumText.text = string.Empty;
		Vector2 anchoredPosition = ItemScrollRect.content.anchoredPosition;
		anchoredPosition.y = 0f;
		ItemScrollRect.content.anchoredPosition = anchoredPosition;
		switch (StorageGroup)
		{
		case StorageGroupType.Bag:
			if (CurrentMode == Mode.BazaarExhibit)
			{
				TabArea.SetActive(value: false);
				EmptyText.enabled = false;
				LoadStorage(DataSourceType.BagMaterial);
				break;
			}
			TabArea.SetActive(value: true);
			AddTab("消費", delegate(bool b)
			{
				if (b)
				{
					LoadStorage(DataSourceType.BagUse);
				}
			});
			AddTab("素材", delegate(bool b)
			{
				if (b)
				{
					LoadStorage(DataSourceType.BagMaterial);
				}
			});
			AddTab("装備品", delegate(bool b)
			{
				if (b)
				{
					LoadStorage(DataSourceType.BagEquip);
				}
			});
			AddTab("ジョブ専用", delegate(bool b)
			{
				if (b)
				{
					LoadStorage(DataSourceType.BagJob);
				}
			});
			break;
		case StorageGroupType.Warehouse:
			TabArea.SetActive(value: true);
			AddTab("通常枠", delegate(bool b)
			{
				if (b)
				{
					LoadStorage(DataSourceType.WerehouseFree);
				}
			});
			AddTab("拡張枠", delegate(bool b)
			{
				if (b)
				{
					LoadStorage(DataSourceType.WerehouseEx);
				}
			});
			break;
		case StorageGroupType.Baggage:
			TabArea.SetActive(value: true);
			AddTab("引出し１", delegate(bool b)
			{
				if (b)
				{
					LoadStorage(DataSourceType.BaggageEx1);
				}
			});
			AddTab("引出し２", delegate(bool b)
			{
				if (b)
				{
					LoadStorage(DataSourceType.BaggageEx2);
				}
			});
			AddTab("引出し３", delegate(bool b)
			{
				if (b)
				{
					LoadStorage(DataSourceType.BaggageEx3);
				}
			});
			break;
		case StorageGroupType.Post:
			TabArea.SetActive(value: false);
			EmptyText.enabled = false;
			LoadStorage(DataSourceType.Post);
			break;
		}
	}

	public void AddDDValue()
	{
		if (NumDD.value < NumDD.options.Count - 1)
		{
			NumDD.value++;
		}
	}

	public void SubDDValue()
	{
		if (NumDD.value > 0)
		{
			NumDD.value--;
		}
	}

	private void AddTab(string Name, Action<bool> onClick)
	{
		GameObject gameObject = UnityEngine.Object.Instantiate(GroupTabBase.gameObject);
		gameObject.SetActive(value: true);
		Toggle component = gameObject.GetComponent<Toggle>();
		RectTransform component2 = gameObject.GetComponent<RectTransform>();
		Vector3 localScale = component2.transform.localScale;
		Vector2 sizeDelta = component2.sizeDelta;
		Vector2 offsetMin = component2.offsetMin;
		Vector2 offsetMax = component2.offsetMax;
		component2.transform.SetParent(GroupTabBase.transform.parent);
		component2.transform.localScale = localScale;
		component2.sizeDelta = sizeDelta;
		component2.offsetMin = offsetMin;
		component2.offsetMax = offsetMax;
		component.GetComponentInChildren<Text>().text = Name;
		component.onValueChanged.AddListener(onClick.Invoke);
		Tabs.Add(component);
	}

	private void LoadStorage(DataSourceType datasourceType)
	{
		SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		ClearPanel();
		SelectedDtataSourceType = datasourceType;
		MaxSlotNum = 40u;
		SlotMin = 1u;
		SlotMax = MaxSlotNum;
		MaxNumText.text = string.Empty;
		if (datasourceType == DataSourceType.BagUse)
		{
			StartCoroutine(ItemStorage.GetBagUseSlotNum(delegate(StorageSlotNum retSlotNum)
			{
				InitializeDD(retSlotNum.SlotNum);
				StartCoroutine(ItemStorage.GetBagUse(UpdateContents, null, CacheOption.OneMinute));
			}, null, CacheOption.OneMinute));
		}
		if (datasourceType == DataSourceType.BagMaterial)
		{
			StartCoroutine(ItemStorage.GetBagMaterialSlotNum(delegate(StorageSlotNum retSlotNum)
			{
				InitializeDD(retSlotNum.SlotNum);
				StartCoroutine(ItemStorage.GetBagMaterial(UpdateContents, null, CacheOption.OneMinute));
			}, null, CacheOption.OneMinute));
		}
		if (datasourceType == DataSourceType.BagEquip)
		{
			StartCoroutine(ItemStorage.GetBagEquipSlotNum(delegate(StorageSlotNum retSlotNum)
			{
				InitializeDD(retSlotNum.SlotNum);
				StartCoroutine(ItemStorage.GetBagEquip(UpdateContents, null, CacheOption.OneMinute));
			}, null, CacheOption.OneMinute));
		}
		if (datasourceType == DataSourceType.BagJob)
		{
			StartCoroutine(ItemStorage.GetBagJobSlotNum(delegate(StorageSlotNum retSlotNum)
			{
				InitializeDD(retSlotNum.SlotNum);
				StartCoroutine(ItemStorage.GetBagJob(UpdateContents, null, CacheOption.OneMinute));
			}, null, CacheOption.OneMinute));
		}
		if (datasourceType == DataSourceType.WerehouseFree)
		{
			StartCoroutine(ItemStorage.GetWarehouseFreeSlotNum(delegate(StorageSlotNum retSlotNum)
			{
				InitializeDD(retSlotNum.SlotNum);
			}, null, CacheOption.OneMinute));
		}
		if (datasourceType == DataSourceType.WerehouseEx)
		{
			StartCoroutine(ItemStorage.GetWarehouseExSlotNum(delegate(StorageSlotNum retSlotNum)
			{
				InitializeDD(retSlotNum.SlotNum);
			}, null, CacheOption.OneMinute));
		}
		if (datasourceType == DataSourceType.BaggageEx1)
		{
			StartCoroutine(ItemStorage.GetBaggageEx1SlotNum(delegate(StorageSlotNum retSlotNum)
			{
				InitializeDD(retSlotNum.SlotNum);
			}, null, CacheOption.OneMinute));
		}
		if (datasourceType == DataSourceType.BaggageEx2)
		{
			StartCoroutine(ItemStorage.GetBaggageEx2SlotNum(delegate(StorageSlotNum retSlotNum)
			{
				InitializeDD(retSlotNum.SlotNum);
			}, null, CacheOption.OneMinute));
		}
		if (datasourceType == DataSourceType.BaggageEx3)
		{
			StartCoroutine(ItemStorage.GetBaggageEx3SlotNum(delegate(StorageSlotNum retSlotNum)
			{
				InitializeDD(retSlotNum.SlotNum);
			}, null, CacheOption.OneMinute));
		}
		if (datasourceType == DataSourceType.Post)
		{
			StartCoroutine(ItemStorage.GetDeliveryBoxSlotNum(delegate(StorageSlotNum retSlotNum)
			{
				InitializeDD(retSlotNum.SlotNum);
			}, null, CacheOption.OneHour));
		}
	}

	private void NumDD_OnValueChanged(int value)
	{
		if (!IsInitializingDD)
		{
			ClearPanel();
			SlotMin = (uint)(value * 40 + 1);
			SlotMax = (uint)(value * 40 + 40);
			if (SlotMax > MaxSlotNum)
			{
				SlotMax = MaxSlotNum;
			}
			if (SelectedDtataSourceType == DataSourceType.WerehouseFree)
			{
				StartCoroutine(ItemStorage.GetWarehouseFree(UpdateContents, null, SlotMin, 40u, CacheOption.OneMinute, LoadingAnimation.Default));
			}
			if (SelectedDtataSourceType == DataSourceType.WerehouseEx)
			{
				StartCoroutine(ItemStorage.GetWarehouseEx(UpdateContents, null, SlotMin, 40u, CacheOption.OneMinute, LoadingAnimation.Default));
			}
			if (SelectedDtataSourceType == DataSourceType.BaggageEx1)
			{
				StartCoroutine(ItemStorage.GetBaggageEx1(UpdateContents, null, SlotMin, 40u, CacheOption.OneMinute, LoadingAnimation.Default));
			}
			if (SelectedDtataSourceType == DataSourceType.BaggageEx2)
			{
				StartCoroutine(ItemStorage.GetBaggageEx2(UpdateContents, null, SlotMin, 40u, CacheOption.OneMinute, LoadingAnimation.Default));
			}
			if (SelectedDtataSourceType == DataSourceType.BaggageEx3)
			{
				StartCoroutine(ItemStorage.GetBaggageEx3(UpdateContents, null, SlotMin, 40u, CacheOption.OneMinute, LoadingAnimation.Default));
			}
			if (SelectedDtataSourceType == DataSourceType.Post)
			{
				StartCoroutine(ItemStorage.GetDeliveryBox(UpdateContents, null, SlotMin, 40u, CacheOption.OneHour, LoadingAnimation.Default));
			}
		}
	}

	private void InitializeDD(uint slotNum)
	{
		IsInitializingDD = true;
		NumDD.options.Clear();
		MaxSlotNum = slotNum;
		uint num = slotNum / 40;
		if (num > 1)
		{
			for (uint num2 = 0u; num2 < num; num2++)
			{
				Dropdown.OptionData optionData = new Dropdown.OptionData();
				optionData.text = num2 + 1 + "/" + num;
				NumDD.options.Add(optionData);
			}
		}
		NumDD.value = 0;
		NumDD.RefreshShownValue();
		MaxNumText.text = MaxSlotNum.ToString();
		IsInitializingDD = false;
		NumDD_OnValueChanged(0);
	}

	private bool ItemFilter(StorageItem item)
	{
		if (CurrentMode == Mode.BazaarExhibit && !item.Item.CanBazaar)
		{
			return false;
		}
		return false;
	}

	private void UpdateContents(CharacterItemStorage storage)
	{
		StorageItem storageItem = new StorageItem();
		int num = 0;
		for (ushort num2 = (ushort)SlotMin; num2 <= SlotMax; num2++)
		{
			if (num < storage.ItemList.Count && storage.ItemList[num].SlotNo == num2)
			{
				AddPanel(storage.StorageType, storage.ItemList[num]);
				num++;
			}
			else
			{
				storageItem.SlotNo = num2;
				AddPanel(storage.StorageType, storageItem);
			}
		}
		EmptyText.enabled = false;
		SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
	}

	private void AddPanel(StorageType storageType, StorageItem item)
	{
		GameObject gameObject = UnityEngine.Object.Instantiate(ItemPanelBase.gameObject);
		gameObject.SetActive(value: true);
		InventoryItemPanel component = gameObject.GetComponent<InventoryItemPanel>();
		RectTransform component2 = gameObject.GetComponent<RectTransform>();
		Vector3 localScale = component2.transform.localScale;
		Vector2 sizeDelta = component2.sizeDelta;
		Vector2 offsetMin = component2.offsetMin;
		Vector2 offsetMax = component2.offsetMax;
		component2.transform.SetParent(ItemPanelBase.transform.parent);
		component2.transform.localScale = localScale;
		component2.sizeDelta = sizeDelta;
		component2.offsetMin = offsetMin;
		component2.offsetMax = offsetMax;
		component.UpdateContent(CurrentMode, storageType, item);
		Panels.Add(component);
	}
}
