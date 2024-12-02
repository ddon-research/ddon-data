using System;

namespace Packet;

[Serializable]
public class MailSent
{
	public ulong Id;

	public string Title;

	public DateTime BaseExpire = default(DateTime);

	public DateTime Created = default(DateTime);
}
