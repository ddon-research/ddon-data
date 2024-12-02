using System;

namespace Packet;

[Serializable]
public class ClientVersionCheckPacket
{
	public PlatformID PlatformID;

	public uint ClientVersion;
}
