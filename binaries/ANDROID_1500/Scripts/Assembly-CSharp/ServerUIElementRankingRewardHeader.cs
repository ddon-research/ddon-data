using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementRankingRewardHeader : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private Text Score;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
		Score.text = DispParam.Text2;
	}
}
