using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class MailReceivedList
{
	public List<MailReceived> Elements = new List<MailReceived>();
}
