using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class CalendarAbstractParam
{
	public List<CalendarAbstract> abstList = new List<CalendarAbstract>();
}
