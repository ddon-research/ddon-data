using System;

namespace Packet;

[Serializable]
public class BazaarItem
{
	public ItemData Item = new ItemData();

	public uint ExhibitNum;
}
