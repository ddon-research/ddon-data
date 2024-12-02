using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementLabel : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
	}
}
