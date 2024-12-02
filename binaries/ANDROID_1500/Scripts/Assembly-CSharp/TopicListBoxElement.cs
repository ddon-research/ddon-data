using UnityEngine;
using UnityEngine.UI;

public class TopicListBoxElement : ListBoxElement<TopicData>
{
	[SerializeField]
	private Text NameLabel;

	public override void UpdateContent(TopicData itemData)
	{
		NameLabel.text = itemData.Name;
	}
}
