using UnityEngine;
using UnityEngine.UI;

public class ChildTextFitter : MonoBehaviour
{
	[SerializeField]
	private Text ChildText;

	[SerializeField]
	private Scrollbar PageScrollbar;

	[SerializeField]
	private AutoLayoutRebuilder MyAutoRebuilder;

	private void Update()
	{
		Fitting();
	}

	public void Fitting()
	{
		RectTransform rectTransform = base.transform as RectTransform;
		float num = ChildText.preferredHeight + ChildText.lineSpacing + (float)ChildText.fontSize;
		float num2 = num + ChildText.rectTransform.offsetMin.y * 2f;
		if (num2 > rectTransform.sizeDelta.y)
		{
			rectTransform.sizeDelta = new Vector2(rectTransform.sizeDelta.x, num2);
			if (PageScrollbar != null)
			{
				PageScrollbar.value = 0f;
			}
			if (MyAutoRebuilder != null)
			{
				MyAutoRebuilder.MarkRebuild();
			}
		}
	}
}
