using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class CraftPawnStatusList
{
	public List<CraftPawnStatus> Statuses = new List<CraftPawnStatus>();
}
