using System;

namespace Packet;

[Serializable]
public class StorageSlot
{
	public StorageType Storage;

	public ushort SlotNo;

	public override bool Equals(object obj)
	{
		if (obj == null || GetType() != obj.GetType())
		{
			return false;
		}
		StorageSlot storageSlot = (StorageSlot)obj;
		return Storage == storageSlot.Storage && SlotNo == storageSlot.SlotNo;
	}

	public override int GetHashCode()
	{
		return ((ushort)Storage << 16) | SlotNo;
	}
}
