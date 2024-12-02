using System;

namespace Packet;

[Serializable]
public class CharacterProfileData
{
	public string FirstName;

	public string LastName;

	public uint IconID;

	public byte Sex;

	public string Title;

	public string EntryJob;

	public ushort Adven;

	public ushort Style;

	public byte Party;

	public string Comment;
}
