using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class ItemDataList
{
	public List<ItemData> ItemList = new List<ItemData>();
}
