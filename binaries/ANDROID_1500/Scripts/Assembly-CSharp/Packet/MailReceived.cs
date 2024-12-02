using System;

namespace Packet;

[Serializable]
public class MailReceived
{
	public ulong Id;

	public sbyte State;

	public byte ItemReceived;

	public uint SenderCharacterId;

	public uint SenderCharacterIconId;

	public string SenderCharacterFirstName;

	public string SenderCharacterLastName;

	public string Name;

	public string Head;

	public long Expire;

	public long Created;
}
