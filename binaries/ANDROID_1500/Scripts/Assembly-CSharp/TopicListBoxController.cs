using System.Collections.Generic;

public class TopicListBoxController : ListBoxController<TopicData>
{
	protected override void Setup(List<TopicData> dataSources)
	{
		dataSources.Add(new TopicData
		{
			Name = "【遠征隊】ホットスポット出現！"
		});
		dataSources.Add(new TopicData
		{
			Name = "【コース】成長サポートコース\u3000残り3日"
		});
		dataSources.Add(new TopicData
		{
			Name = "【イベント】グランドミッション開催中"
		});
		dataSources.Add(new TopicData
		{
			Name = "【ＰＲ】90日コース販売中"
		});
	}
}
