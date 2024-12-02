using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementStateLabel : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private Image StateImage;

	[SerializeField]
	private Sprite[] Sprites;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
		ulong param = DispParam.Param1;
		if ((long)param >= 1L && (long)param <= 3L)
		{
			switch (param - 1)
			{
			case 0uL:
			case 1uL:
			case 2uL:
				StateImage.sprite = Sprites[DispParam.Param1 - 1];
				break;
			}
		}
	}
}
