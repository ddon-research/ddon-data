using System;

namespace Packet;

[Serializable]
public class ItemData
{
	public uint ItemID;

	public byte Rank;

	public string Name;

	public string IconName;

	public uint IconColorId;

	public bool CanBazaar;
}
