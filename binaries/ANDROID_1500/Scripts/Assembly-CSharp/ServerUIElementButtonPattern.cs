using Packet;
using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementButtonPattern : ServerUIElementBase
{
	[SerializeField]
	private Button[] Buttons;

	public override void SetupElement()
	{
		int num = (int)DispParam.Param1;
		if (num < Buttons.Length)
		{
			Buttons[num].gameObject.SetActive(value: true);
			Text componentInChildren = Buttons[num].gameObject.GetComponentInChildren<Text>();
			if (componentInChildren != null)
			{
				componentInChildren.text = DispParam.Text1;
			}
			if (Link == LinkType.INVALID)
			{
				Buttons[num].enabled = false;
			}
		}
	}
}
