using System;

namespace Packet;

[Serializable]
public class ClientVersionCheckResultPacket
{
	public bool IsOk;

	public string Url = string.Empty;

	public uint TosVersion;

	public string TosUrl;

	public string StoreUrl;
}
