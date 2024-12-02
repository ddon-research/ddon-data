using Packet;
using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementEventList : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private Text ScheduleLabel;

	[SerializeField]
	private Text StateLabel;

	[SerializeField]
	private Image StateImage;

	[SerializeField]
	private Image Icon;

	[SerializeField]
	private Button Button;

	[SerializeField]
	private Sprite[] StateSprites;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
		ScheduleLabel.text = DispParam.Text2;
		switch (DispParam.Param1)
		{
		case 1uL:
			StateLabel.text = "開催中";
			StateImage.sprite = StateSprites[DispParam.Param1 - 1];
			break;
		case 2uL:
			StateLabel.text = "集計中";
			StateImage.sprite = StateSprites[DispParam.Param1 - 1];
			break;
		case 3uL:
			StateLabel.text = "ランキング確定";
			StateImage.sprite = StateSprites[DispParam.Param1 - 1];
			break;
		}
		Icon.enabled = DispParam.Param2 != 0;
		if (Link == LinkType.INVALID)
		{
			Button.enabled = false;
		}
	}
}
