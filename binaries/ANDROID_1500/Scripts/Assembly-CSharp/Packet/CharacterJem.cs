using System;

namespace Packet;

[Serializable]
public class CharacterJem
{
	public PlatformID PlatformId;

	public JemType Type;

	public ulong Value;
}
