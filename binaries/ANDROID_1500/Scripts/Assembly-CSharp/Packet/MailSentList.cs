using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class MailSentList
{
	public List<MailSent> Elements = new List<MailSent>();
}
