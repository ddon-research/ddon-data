using System;

namespace Packet;

[Serializable]
public class StorageSlotItem
{
	public StorageSlot Address = new StorageSlot();

	public ItemData Item = new ItemData();

	public uint Num;
}
