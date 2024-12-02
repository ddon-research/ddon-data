using System;
using System.Collections.Generic;
using Packet;

[Serializable]
public class CalendarUpdateInfoPackage
{
	public List<CalendarUpdateInfo> ClanReadList = new List<CalendarUpdateInfo>();

	public List<CalendarUpdateInfo> OfficialReadList = new List<CalendarUpdateInfo>();

	public CalendarUpdateInfo ClanBoard;
}
