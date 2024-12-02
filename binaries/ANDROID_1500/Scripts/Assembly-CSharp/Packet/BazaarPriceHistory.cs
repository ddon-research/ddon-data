using System;

namespace Packet;

[Serializable]
public class BazaarPriceHistory
{
	public uint ItemId;

	public uint Price;

	public ushort Num;

	public long Created;
}
