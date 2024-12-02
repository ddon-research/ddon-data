using Packet;
using UnityEngine;
using UnityEngine.UI;

public class HomeTopicTableViewCell : TableViewCell<HomeTopics.Topic>
{
	[SerializeField]
	private Text Time;

	[SerializeField]
	private new Text Title;

	[SerializeField]
	private new Image Icon;

	public override void UpdateContent(HomeTopics.Topic itemData)
	{
		Title.text = itemData.Title;
		Time.text = itemData.Time.ToString();
	}
}
