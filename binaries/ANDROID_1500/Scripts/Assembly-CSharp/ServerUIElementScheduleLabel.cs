using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementScheduleLabel : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
		if (DispParam.Param1 != 0)
		{
			RectTransform component = GetComponent<RectTransform>();
			component.sizeDelta = new Vector2(component.sizeDelta.x, DispParam.Param1);
		}
	}
}
