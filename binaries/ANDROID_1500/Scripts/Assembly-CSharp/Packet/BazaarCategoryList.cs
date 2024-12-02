using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class BazaarCategoryList
{
	public List<BazaarCategory> Categories = new List<BazaarCategory>();
}
