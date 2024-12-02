using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementBaseLevel : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private Shadow LabelShadow;

	[SerializeField]
	private Image[] Images;

	[SerializeField]
	private Sprite ExtraSprite;

	public override void SetupElement()
	{
		if (DispParam.Param1 != 0)
		{
			Image[] images = Images;
			foreach (Image image in images)
			{
				image.sprite = ExtraSprite;
			}
			LabelShadow.effectColor = Color.black;
		}
		Label.text = DispParam.Text1;
		LayoutRebuilder.ForceRebuildLayoutImmediate(base.transform as RectTransform);
	}
}
