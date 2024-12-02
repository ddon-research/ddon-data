using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class ClanMemberList
{
	public List<ClanMemberListElement> Members = new List<ClanMemberListElement>();

	public List<uint> OnlineCharacterIDs = new List<uint>();
}
