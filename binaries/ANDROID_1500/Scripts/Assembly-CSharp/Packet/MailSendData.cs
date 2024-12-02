using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class MailSendData
{
	public List<uint> ToCharacterIDs = new List<uint>();

	public string Title;

	public string Text;
}
