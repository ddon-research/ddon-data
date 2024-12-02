using System;

namespace Packet;

[Serializable]
public class MailSentDetail
{
	public ulong Id;

	public string Title;

	public string Text;

	public DateTime BaseExpire;

	public DateTime Created;
}
