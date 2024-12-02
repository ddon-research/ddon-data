using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class CalendarUpdateInfoListParam
{
	public List<CalendarUpdateInfo> infoList = new List<CalendarUpdateInfo>();
}
