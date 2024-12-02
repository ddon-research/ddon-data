using System;

namespace Packet;

[Serializable]
public class ClanMemberListElement : CharacterMemberListElement
{
	public uint MemberRank;

	public uint Permission;
}
