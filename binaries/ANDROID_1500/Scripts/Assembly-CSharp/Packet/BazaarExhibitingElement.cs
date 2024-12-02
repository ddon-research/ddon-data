using System;

namespace Packet;

[Serializable]
public class BazaarExhibitingElement
{
	public ulong ID;

	public E_BAZAAR_STATE Status;

	public ItemData Item = new ItemData();

	public long RemainTime;

	public ushort Num;

	public uint UnitPrice;

	public uint Proceeds;
}
