using DDOAppMaster.Enum;
using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementExplain : ServerUIElementBase
{
	[SerializeField]
	private Text Label1;

	[SerializeField]
	private Text Label2;

	[SerializeField]
	private AutoLayoutRebuilder MyRebuilder;

	public override void SetupElement()
	{
		Label1.text = DispParam.Text1;
		if (DispParam.Text1.Length == 0)
		{
			Label1.gameObject.SetActive(value: false);
		}
		Label2.text = DispParam.Text2;
		if (DispParam.Text2.Length == 0)
		{
			Label2.gameObject.SetActive(value: false);
		}
		switch ((ExplainTextAlign)DispParam.Param1)
		{
		case ExplainTextAlign.CENTER:
			Label1.alignment = TextAnchor.MiddleCenter;
			break;
		case ExplainTextAlign.LEFT:
			Label1.alignment = TextAnchor.MiddleLeft;
			break;
		case ExplainTextAlign.RIGHT:
			Label1.alignment = TextAnchor.MiddleRight;
			break;
		}
		MyRebuilder.MarkRebuild();
	}
}
