using DDOAppMaster.Enum;
using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementTitle : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private QuestIcon QuestIcon;

	[SerializeField]
	private GameObject ClearIcon;

	[SerializeField]
	private Image BG;

	[SerializeField]
	private Color ExtraColor;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
		if (DispParam.Param1 != 0)
		{
			QuestIcon.gameObject.SetActive(value: true);
			QuestIcon.Setup((QuestIconType)DispParam.Param1);
		}
		else
		{
			QuestIcon.gameObject.SetActive(value: false);
		}
		ClearIcon.SetActive(value: false);
		if (DispParam.Text2.Length > 0)
		{
			ClearIcon.SetActive(value: true);
		}
		if (DispParam.Param2 != 0)
		{
			BG.color = ExtraColor;
		}
		LayoutRebuilder.ForceRebuildLayoutImmediate(base.transform as RectTransform);
	}
}
