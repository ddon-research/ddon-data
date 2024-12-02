using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementRankingBody : ServerUIElementBase
{
	[SerializeField]
	private Text Rank;

	[SerializeField]
	private Text Name;

	[SerializeField]
	private Text Score;

	[SerializeField]
	private Image RankImage;

	[SerializeField]
	private Text BestRank;

	[SerializeField]
	private Sprite[] RankSprites;

	public override void SetupElement()
	{
		Name.text = DispParam.Text1;
		Score.text = DispParam.Param2.ToString("#,0") + "pt";
		if (DispParam.Param1 >= 1 && DispParam.Param1 <= 3)
		{
			BestRank.text = DispParam.Param1.ToString();
			Rank.gameObject.SetActive(value: false);
			RankImage.sprite = RankSprites[DispParam.Param1 - 1];
		}
		else
		{
			Rank.text = DispParam.Param1.ToString();
			RankImage.gameObject.SetActive(value: false);
			RectTransform rectTransform = base.transform as RectTransform;
			rectTransform.sizeDelta = new Vector2(rectTransform.sizeDelta.x, 70f);
		}
	}
}
