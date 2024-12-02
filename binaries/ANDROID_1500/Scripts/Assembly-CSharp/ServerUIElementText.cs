using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementText : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private Text SubLabel;

	[SerializeField]
	private GameObject Empty;

	public override void SetupElement()
	{
		if (DispParam.Text1 == string.Empty)
		{
			Label.gameObject.SetActive(value: false);
			Empty.SetActive(value: false);
		}
		if (DispParam.Text2 == string.Empty)
		{
			SubLabel.gameObject.SetActive(value: false);
			Empty.SetActive(value: false);
		}
		if (DispParam.Param1 != 0)
		{
			Label.alignment = TextAnchor.UpperCenter;
			SubLabel.alignment = TextAnchor.UpperCenter;
		}
		Label.text = DispParam.Text1;
		SubLabel.text = DispParam.Text2;
		LayoutRebuilder.ForceRebuildLayoutImmediate(base.transform as RectTransform);
	}
}
