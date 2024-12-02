using System;
using System.Collections.Generic;
using Packet;

public class HomeTopicTableViewController : TableViewController<HomeTopics.Topic>
{
	private new void Start()
	{
		base.Start();
		LoadData();
	}

	public void LoadData()
	{
		TableData = new List<HomeTopics.Topic>
		{
			new HomeTopics.Topic
			{
				Title = "適当に集合してゴブリン狩り",
				Time = DateTime.Now,
				Type = HomeTopics.Topic.TopicType.Clan
			},
			new HomeTopics.Topic
			{
				Title = "定期サーバーメンテナンス",
				Time = DateTime.Now,
				Type = HomeTopics.Topic.TopicType.System
			},
			new HomeTopics.Topic
			{
				Title = "定期サーバーメンテナンス",
				Time = DateTime.Now,
				Type = HomeTopics.Topic.TopicType.System
			}
		};
		UpdateContents();
	}

	protected override float CellHeightAtIndex(int index)
	{
		return 80f;
	}
}
