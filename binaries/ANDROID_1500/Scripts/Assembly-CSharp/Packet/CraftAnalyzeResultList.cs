using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class CraftAnalyzeResultList
{
	public List<CraftAnalyzeResult> List = new List<CraftAnalyzeResult>();
}
