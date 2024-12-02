using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementCaution : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private Image BG;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
		RectTransform component = GetComponent<RectTransform>();
		ContentSizeFitter component2 = GetComponent<ContentSizeFitter>();
		if (component2 != null && DispParam.Param1 != 0)
		{
			component2.verticalFit = ContentSizeFitter.FitMode.Unconstrained;
			component.sizeDelta = new Vector2(component.sizeDelta.x, DispParam.Param1);
		}
		if (DispParam.Text2 != string.Empty)
		{
			Color color = Color.black;
			if (ColorUtility.TryParseHtmlString(DispParam.Text2, out color))
			{
				BG.sprite = null;
				BG.color = color;
			}
		}
		LayoutRebuilder.ForceRebuildLayoutImmediate(component);
	}
}
