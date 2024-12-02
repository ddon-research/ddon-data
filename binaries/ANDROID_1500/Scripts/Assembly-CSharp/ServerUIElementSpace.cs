using UnityEngine;

public class ServerUIElementSpace : ServerUIElementBase
{
	public override void SetupElement()
	{
		RectTransform component = GetComponent<RectTransform>();
		component.sizeDelta = new Vector2(component.sizeDelta.x, DispParam.Param1);
	}
}
