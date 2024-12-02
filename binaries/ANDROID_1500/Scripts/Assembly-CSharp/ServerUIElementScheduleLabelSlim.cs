using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementScheduleLabelSlim : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
	}
}
