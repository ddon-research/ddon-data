using UnityEngine;
using UnityEngine.UI;

namespace Assets.Script.ServerUI;

internal class ServerUIElementHeader : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
		LayoutRebuilder.ForceRebuildLayoutImmediate(base.transform as RectTransform);
	}
}
