using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementFooterRankInfo : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private Text Rank;

	[SerializeField]
	private Text Score;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
		if (DispParam.Param1 == 0)
		{
			Rank.text = "- 位";
		}
		else
		{
			Rank.text = DispParam.Param1 + "位";
		}
		Score.text = DispParam.Param2.ToString("#,0") + "pt";
	}
}
