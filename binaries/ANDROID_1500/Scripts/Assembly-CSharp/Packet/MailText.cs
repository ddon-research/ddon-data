using System;

namespace Packet;

[Serializable]
public class MailText : MailReceived
{
	public string Text;
}
