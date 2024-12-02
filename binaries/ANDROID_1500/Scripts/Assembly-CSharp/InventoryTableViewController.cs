using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

[RequireComponent(typeof(ScrollRect))]
[RequireComponent(typeof(CanvasGroup))]
public class InventoryTableViewController : TableViewController<InventoryData>
{
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

	[SerializeField]
	private DataSourceType SourceType;

	private uint MaxSlotNum;

	private uint LoadedSlotNum;

	private const uint LoadNumAtOnce = 40u;

	[SerializeField]
	private NavigationViewController navigationView;

	[SerializeField]
	private ViewController contentView;

	private void LoadData()
	{
		Initialize();
		LoadedSlotNum = 1u;
		if (SourceType == DataSourceType.BagUse)
		{
			StartCoroutine(ItemStorage.GetBagUse(delegate(CharacterItemStorage ret)
			{
				AddStorageData(40u);
				OnPacketStorageData(ret);
			}, null, null, LoadingAnimation.Default));
		}
		if (SourceType == DataSourceType.BagMaterial)
		{
			StartCoroutine(ItemStorage.GetBagMaterial(delegate(CharacterItemStorage ret)
			{
				AddStorageData(40u);
				OnPacketStorageData(ret);
			}, null, null, LoadingAnimation.Default));
		}
		if (SourceType == DataSourceType.BagEquip)
		{
			StartCoroutine(ItemStorage.GetBagEquip(delegate(CharacterItemStorage ret)
			{
				AddStorageData(40u);
				OnPacketStorageData(ret);
			}, null, null, LoadingAnimation.Default));
		}
		if (SourceType == DataSourceType.BagJob)
		{
			StartCoroutine(ItemStorage.GetBagJob(delegate(CharacterItemStorage ret)
			{
				AddStorageData(40u);
				OnPacketStorageData(ret);
			}, null, null, LoadingAnimation.Default));
		}
		if (SourceType == DataSourceType.WerehouseFree)
		{
			StartCoroutine(ItemStorage.GetWarehouseFreeSlotNum(delegate(StorageSlotNum retSlotNum)
			{
				MaxSlotNum = retSlotNum.SlotNum;
				GetWarehouseFree();
			}, null, null, LoadingAnimation.Default));
		}
		if (SourceType == DataSourceType.WerehouseEx)
		{
			StartCoroutine(ItemStorage.GetWarehouseExSlotNum(delegate(StorageSlotNum retSlotNum)
			{
				MaxSlotNum = retSlotNum.SlotNum;
				GetWarehouseEx();
			}, null, null, LoadingAnimation.Default));
		}
		if (SourceType == DataSourceType.BaggageEx1)
		{
			StartCoroutine(ItemStorage.GetBaggageEx1SlotNum(delegate(StorageSlotNum retSlotNum)
			{
				MaxSlotNum = retSlotNum.SlotNum;
				GetBaggageEx1();
			}, null, null, LoadingAnimation.Default));
		}
		if (SourceType == DataSourceType.BaggageEx2)
		{
			StartCoroutine(ItemStorage.GetBaggageEx2SlotNum(delegate(StorageSlotNum retSlotNum)
			{
				MaxSlotNum = retSlotNum.SlotNum;
				GetBaggageEx2();
			}, null, null, LoadingAnimation.Default));
		}
		if (SourceType == DataSourceType.BaggageEx3)
		{
			StartCoroutine(ItemStorage.GetBaggageEx3SlotNum(delegate(StorageSlotNum retSlotNum)
			{
				MaxSlotNum = retSlotNum.SlotNum;
				GetBaggageEx3();
			}, null, null, LoadingAnimation.Default));
		}
		if (SourceType == DataSourceType.Post)
		{
			StartCoroutine(ItemStorage.GetDeliveryBoxSlotNum(delegate(StorageSlotNum retSlotNum)
			{
				MaxSlotNum = retSlotNum.SlotNum;
				GetPost();
			}, null, null, LoadingAnimation.Default));
		}
	}

	private void AddStorageData(uint SlotNum)
	{
		for (uint num = 0u; num < SlotNum; num++)
		{
			TableData.Add(new InventoryData((uint)(TableData.Count + 1)));
		}
	}

	public void OnPacketStorageData(CharacterItemStorage storage)
	{
		foreach (StorageItem item in storage.ItemList)
		{
			TableData[item.SlotNo - 1].SetFromPacket(item);
		}
		UpdateContents();
	}

	public void GetWarehouseFree()
	{
		if (base.CachedCanvasGroup.interactable)
		{
			base.CachedCanvasGroup.interactable = false;
			AddStorageData(40u);
			StartCoroutine(ItemStorage.GetWarehouseFree(delegate(CharacterItemStorage ret)
			{
				OnPacketStorageData(ret);
				base.CachedCanvasGroup.interactable = true;
			}, null, LoadedSlotNum, 40u, null, LoadingAnimation.Default));
			LoadedSlotNum += 40u;
		}
	}

	public void GetWarehouseEx()
	{
		if (base.CachedCanvasGroup.interactable)
		{
			base.CachedCanvasGroup.interactable = false;
			AddStorageData(40u);
			StartCoroutine(ItemStorage.GetWarehouseEx(delegate(CharacterItemStorage ret)
			{
				OnPacketStorageData(ret);
				base.CachedCanvasGroup.interactable = true;
			}, null, LoadedSlotNum, 40u, null, LoadingAnimation.Default));
			LoadedSlotNum += 40u;
		}
	}

	public void GetBaggageEx1()
	{
		if (base.CachedCanvasGroup.interactable)
		{
			base.CachedCanvasGroup.interactable = false;
			AddStorageData(40u);
			StartCoroutine(ItemStorage.GetBaggageEx1(delegate(CharacterItemStorage ret)
			{
				OnPacketStorageData(ret);
				base.CachedCanvasGroup.interactable = true;
			}, null, LoadedSlotNum, 40u, null, LoadingAnimation.Default));
			LoadedSlotNum += 40u;
		}
	}

	public void GetBaggageEx2()
	{
		if (base.CachedCanvasGroup.interactable)
		{
			base.CachedCanvasGroup.interactable = false;
			AddStorageData(40u);
			StartCoroutine(ItemStorage.GetBaggageEx2(delegate(CharacterItemStorage ret)
			{
				OnPacketStorageData(ret);
				base.CachedCanvasGroup.interactable = true;
			}, null, LoadedSlotNum, 40u, null, LoadingAnimation.Default));
			LoadedSlotNum += 40u;
		}
	}

	public void GetBaggageEx3()
	{
		if (base.CachedCanvasGroup.interactable)
		{
			base.CachedCanvasGroup.interactable = false;
			AddStorageData(40u);
			StartCoroutine(ItemStorage.GetBaggageEx3(delegate(CharacterItemStorage ret)
			{
				OnPacketStorageData(ret);
				base.CachedCanvasGroup.interactable = true;
			}, null, LoadedSlotNum, 40u, null, LoadingAnimation.Default));
			LoadedSlotNum += 40u;
		}
	}

	public void GetPost()
	{
		if (base.CachedCanvasGroup.interactable)
		{
			base.CachedCanvasGroup.interactable = false;
			AddStorageData(40u);
			StartCoroutine(ItemStorage.GetDeliveryBox(delegate(CharacterItemStorage ret)
			{
				OnPacketStorageData(ret);
				base.CachedCanvasGroup.interactable = true;
			}, null, LoadedSlotNum, 40u, null, LoadingAnimation.Default));
			LoadedSlotNum += 40u;
		}
	}

	protected override void OnViewLastCell()
	{
		Debug.Log("OnViewLastCell");
		if (LoadedSlotNum < MaxSlotNum)
		{
			if (SourceType == DataSourceType.WerehouseFree)
			{
				GetWarehouseFree();
			}
			else if (SourceType == DataSourceType.WerehouseEx)
			{
				GetWarehouseEx();
			}
			else if (SourceType == DataSourceType.BaggageEx1)
			{
				GetBaggageEx1();
			}
			else if (SourceType == DataSourceType.BaggageEx2)
			{
				GetBaggageEx2();
			}
			else if (SourceType == DataSourceType.BaggageEx3)
			{
				GetBaggageEx3();
			}
			else if (SourceType == DataSourceType.Post)
			{
				GetPost();
			}
			base.OnViewLastCell();
		}
	}

	protected override void Awake()
	{
		base.Awake();
	}

	protected override void Start()
	{
		base.Start();
		if (navigationView != null)
		{
			navigationView.Push(this);
		}
	}

	private void OnEnable()
	{
		LoadData();
	}

	public void OnPressCell(MainMenuTableViewCell cell)
	{
		if (navigationView != null)
		{
			navigationView.Push(contentView);
		}
	}
}
