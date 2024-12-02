using Packet;

public class InventoryData
{
	public uint SlotNo;

	public uint ItemID;

	public string ItemName;

	public uint ItemNum;

	public bool IsEmpty;

	public InventoryData(uint slotNo)
	{
		SlotNo = slotNo;
		IsEmpty = true;
	}

	public InventoryData(StorageItem item)
	{
		SetFromPacket(item);
		IsEmpty = false;
	}

	public void SetFromPacket(StorageItem item)
	{
		SlotNo = item.SlotNo;
		ItemName = item.Item.Name;
		ItemID = item.Item.ItemID;
		ItemNum = item.Num;
		IsEmpty = false;
	}
}
