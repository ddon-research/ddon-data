using Packet;
using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementList : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private Text SubLabel;

	[SerializeField]
	private Button LabelButton;

	[SerializeField]
	private Image Arrow;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
		SubLabel.text = DispParam.Text2;
		if (Link == LinkType.INVALID)
		{
			LabelButton.enabled = false;
			Arrow.enabled = false;
		}
	}
}
