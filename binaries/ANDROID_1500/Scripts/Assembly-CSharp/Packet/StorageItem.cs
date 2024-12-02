using System;

namespace Packet;

[Serializable]
public class StorageItem
{
	public ItemData Item = new ItemData();

	public uint Num;

	public ushort SlotNo;
}
