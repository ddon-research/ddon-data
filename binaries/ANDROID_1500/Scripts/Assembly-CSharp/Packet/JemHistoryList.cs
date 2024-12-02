using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class JemHistoryList
{
	public List<JemHistory> History = new List<JemHistory>();
}
