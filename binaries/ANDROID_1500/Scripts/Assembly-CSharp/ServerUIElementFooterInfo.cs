using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementFooterInfo : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private Text SubLabel;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
		SubLabel.text = DispParam.Text2;
	}
}
