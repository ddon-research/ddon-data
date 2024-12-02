using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class CalendarTopicParam
{
	public List<CalendarTopic> TopicList = new List<CalendarTopic>();

	public uint TopicSizeMax;
}
