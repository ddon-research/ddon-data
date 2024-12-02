using System;

namespace Packet;

[Serializable]
public class CharacterDataBase
{
	public uint CharacterID;

	public uint IconID;

	public string FirstName;

	public string LastName;

	public string ClanName;

	public uint Gold;

	public CharacterJemList Jem;

	public uint GiftNum;

	public byte JobID;

	public ushort JobLv;

	public uint Exp;

	public bool canCraft;

	public long EventTime;
}
