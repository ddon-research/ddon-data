using Packet;

public class BazaarExhibitStatusTableViewController : TableViewController<BazaarExhibitingElement>
{
	public void SetData(BazaarExhibitingStatus status)
	{
		foreach (BazaarExhibitingElement element in status.Elements)
		{
			TableData.Add(element);
		}
		UpdateContents();
	}
}
