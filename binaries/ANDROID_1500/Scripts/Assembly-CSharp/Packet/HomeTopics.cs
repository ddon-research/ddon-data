using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class HomeTopics
{
	[Serializable]
	public class Topic
	{
		public enum TopicType
		{
			Clan,
			System
		}

		public string Title;

		public TopicType Type;

		public DateTime Time;
	}

	public List<Topic> Topics;
}
