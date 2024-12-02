using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class BazaarItemList
{
	public bool IsTooManyResult;

	public List<BazaarItem> Items = new List<BazaarItem>();
}
