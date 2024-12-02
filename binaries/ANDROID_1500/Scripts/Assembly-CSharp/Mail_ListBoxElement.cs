using UnityEngine;
using UnityEngine.UI;

public class Mail_ListBoxElement : ListBoxElement<Mail_ListBoxData>
{
	[SerializeField]
	private Text Label;

	public override void UpdateContent(Mail_ListBoxData itemData)
	{
		if (itemData.IsReceived)
		{
			Label.text = "【受取済】" + itemData.Name;
		}
		else
		{
			Label.text = itemData.Name;
		}
	}
}
