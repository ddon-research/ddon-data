using System;

namespace Packet;

[Serializable]
public class CharacterMemberListElement
{
	public uint CharacterID;

	public uint IconID;

	public string FirstName;

	public string LastName;

	public uint CurrentJobID;

	public uint CurrentJobLv;
}
