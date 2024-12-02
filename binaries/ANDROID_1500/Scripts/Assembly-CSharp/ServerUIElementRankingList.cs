using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementRankingList : ServerUIElementBase
{
	[SerializeField]
	private Text Rank;

	[SerializeField]
	private Text Score;

	public override void SetupElement()
	{
		if (Rank != null)
		{
			Rank.text = DispParam.Text1;
		}
		if (Score != null)
		{
			Score.text = DispParam.Text2;
		}
	}
}
