using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementGage : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private Image Gage;

	public override void SetupElement()
	{
		Label.text = DispParam.Param1 + " / " + DispParam.Param2;
		float num = 0f;
		if (DispParam.Param2 != 0)
		{
			num = (float)DispParam.Param1 / (float)DispParam.Param2;
		}
		if (num > 1f)
		{
			num = 1f;
		}
		if (num > 0f)
		{
			Gage.transform.localScale = new Vector3(num, 1f, 1f);
		}
		else
		{
			Gage.enabled = false;
		}
	}
}
