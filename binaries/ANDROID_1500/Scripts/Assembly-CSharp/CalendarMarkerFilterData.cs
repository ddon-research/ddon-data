using System;
using Packet;

[Serializable]
public class CalendarMarkerFilterData
{
	public CalendarTopic.CALENDAR_TYPE CalType;

	public bool IsEnable;

	public CalendarController.MARKER_FILTER_TYPE FilterType;
}
