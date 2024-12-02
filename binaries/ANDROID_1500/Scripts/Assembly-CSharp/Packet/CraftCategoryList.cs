using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class CraftCategoryList
{
	public List<CraftCategory> Categories = new List<CraftCategory>();
}
