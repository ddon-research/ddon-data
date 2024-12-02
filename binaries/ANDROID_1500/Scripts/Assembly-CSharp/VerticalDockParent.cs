using UnityEngine;

public class VerticalDockParent : ViewController
{
	[SerializeField]
	private RectTransform Parent;

	[SerializeField]
	private float Spacing;

	private void Update()
	{
		Vector2 anchoredPosition = base.CachedRectTransform.anchoredPosition;
		anchoredPosition.y = Parent.anchoredPosition.y - Parent.sizeDelta.y - Spacing;
		base.CachedRectTransform.anchoredPosition = anchoredPosition;
	}
}
