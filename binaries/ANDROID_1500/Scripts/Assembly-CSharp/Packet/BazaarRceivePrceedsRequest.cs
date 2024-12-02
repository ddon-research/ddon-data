using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class BazaarRceivePrceedsRequest
{
	public List<ulong> IDList = new List<ulong>();
}
