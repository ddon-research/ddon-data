using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class BazaarExhibitingStatus
{
	public List<BazaarExhibitingElement> Elements = new List<BazaarExhibitingElement>();
}
