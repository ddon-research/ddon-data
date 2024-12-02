using UnityEngine;
using UnityEngine.UI;

namespace Assets.Script.ServerUI;

internal class ServerUIElementTableSingle : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private Text Content;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
		Content.text = DispParam.Text2;
		LayoutRebuilder.ForceRebuildLayoutImmediate(base.transform as RectTransform);
	}
}
