using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class CalendarUpdateInfoParam
{
	public List<CalendarUpdateInfo> OfficialList = new List<CalendarUpdateInfo>();

	public List<CalendarUpdateInfo> ClanList = new List<CalendarUpdateInfo>();

	public CalendarUpdateInfo ClanBoard = new CalendarUpdateInfo();

	public uint PrivateTopicNum;

	public uint PrivateTopicMax;

	public uint ClanTopicMax;

	public uint OfficialTopicMax;

	public bool IsClanMember;
}
