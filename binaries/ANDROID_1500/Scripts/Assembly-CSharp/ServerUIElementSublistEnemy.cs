using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementSublistEnemy : ServerUIElementBase
{
	[SerializeField]
	private Text Level;

	[SerializeField]
	private Text Name;

	[SerializeField]
	private Text Rank;

	public override void SetupElement()
	{
		Level.text = "LV." + DispParam.Param1;
		Name.text = DispParam.Text1;
		Rank.text = "Rank " + DispParam.Param2 + "～";
	}
}
