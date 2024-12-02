using System;

namespace Packet;

[Serializable]
public class CraftRecipeMaterial
{
	public ItemData Item = new ItemData();

	public uint Num;
}
