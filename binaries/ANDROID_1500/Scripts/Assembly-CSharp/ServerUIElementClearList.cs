using Packet;
using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementClearList : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private Button LabelButton;

	[SerializeField]
	private Image Icon;

	[SerializeField]
	private Image Arrow;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
		if (DispParam.Param1 != 0)
		{
			Icon.enabled = true;
		}
		else
		{
			Icon.enabled = false;
		}
		if (Link == LinkType.INVALID)
		{
			LabelButton.enabled = false;
			Arrow.enabled = false;
		}
	}
}
