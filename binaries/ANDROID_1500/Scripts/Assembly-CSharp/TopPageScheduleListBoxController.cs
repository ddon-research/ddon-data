using System;
using System.Collections.Generic;

public class TopPageScheduleListBoxController : ListBoxController<TopPageScheduleData>
{
	protected override void Setup(List<TopPageScheduleData> dataSources)
	{
		dataSources.Add(new TopPageScheduleData
		{
			Date = new DateTime(2017, 8, 1),
			Name = "ＢＯ周回鍵持ち寄り"
		});
		dataSources.Add(new TopPageScheduleData
		{
			Date = new DateTime(2017, 8, 3),
			Name = "行ける人ＧＭ"
		});
		dataSources.Add(new TopPageScheduleData
		{
			Date = new DateTime(2017, 8, 11),
			Name = "本気でタイムアタック"
		});
		dataSources.Add(new TopPageScheduleData
		{
			Date = new DateTime(2017, 8, 20),
			Name = "抗議デモ"
		});
	}
}
