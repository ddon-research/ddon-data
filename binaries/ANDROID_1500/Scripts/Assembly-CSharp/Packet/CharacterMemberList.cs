using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class CharacterMemberList
{
	public List<CharacterMemberListElement> Members = new List<CharacterMemberListElement>();

	public List<uint> OnlineCharacterIDs = new List<uint>();
}
