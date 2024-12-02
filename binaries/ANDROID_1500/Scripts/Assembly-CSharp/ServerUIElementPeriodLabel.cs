using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementPeriodLabel : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private Text Period;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
		Period.text = DispParam.Text2;
	}
}
