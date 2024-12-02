using System.Collections.Generic;
using Packet;

public class CalendarUpdateInfoPackageDictionary
{
	public Dictionary<ulong, CalendarUpdateInfo> ClanReadList = new Dictionary<ulong, CalendarUpdateInfo>();

	public Dictionary<ulong, CalendarUpdateInfo> OfficialReadList = new Dictionary<ulong, CalendarUpdateInfo>();

	public CalendarUpdateInfo ClanBoard;
}
