using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementSubLabel : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private Text Label2;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
		Label2.text = DispParam.Text2;
		LayoutRebuilder.ForceRebuildLayoutImmediate(base.transform as RectTransform);
	}
}
