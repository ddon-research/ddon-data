using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class BazaarPriceHistoryList
{
	public List<BazaarPriceHistory> HistoryList = new List<BazaarPriceHistory>();
}
