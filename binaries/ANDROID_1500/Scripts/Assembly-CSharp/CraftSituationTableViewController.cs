using Packet;
using WebRequest;

public class CraftSituationTableViewController : TableViewController<CraftPawnStatus>
{
	private void OnEnable()
	{
		LoadData();
	}

	public void LoadData()
	{
		Initialize();
		StartCoroutine(Craft.GetPawnStatus(delegate(CraftPawnStatusList res)
		{
			foreach (CraftPawnStatus status in res.Statuses)
			{
				TableData.Add(status);
			}
			UpdateContents();
		}, null, CacheOption.OneMinute, LoadingAnimation.Default));
	}
}
