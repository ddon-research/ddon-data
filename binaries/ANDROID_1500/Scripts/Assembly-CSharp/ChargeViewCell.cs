using System;
using Packet;
using UnityEngine;
using UnityEngine.UI;

public class ChargeViewCell : MonoBehaviour
{
	public enum BgType
	{
		Pattern00,
		Pattern01
	}

	[SerializeField]
	private Sprite[] BgTypePattern;

	[SerializeField]
	private Text DateText;

	[SerializeField]
	private Text DescText;

	[SerializeField]
	private Text FreeText;

	[SerializeField]
	private Text PayText;

	[SerializeField]
	private Image[] Bgs;

	private JemHistory Data;

	public void UpdateContent(JemHistory itemData, BgType bgType)
	{
		Data = itemData;
		DateTime dateTime = new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc).AddSeconds(itemData.Created).ToLocalTime();
		DateText.text = dateTime.ToString("yyyy.MM.dd\nHH:mm");
		DescText.text = SingletonMonoBehaviour<ChargeManager>.Instance.GetActivitieName(itemData.Activitie);
		FreeText.text = itemData.FreeValue.ToString("N0");
		if (itemData.FreeValue > 0)
		{
			FreeText.text = "+" + FreeText.text;
		}
		PayText.text = itemData.PayValue.ToString("N0");
		if (itemData.PayValue > 0)
		{
			PayText.text = "+" + PayText.text;
		}
		Image[] bgs = Bgs;
		foreach (Image image in bgs)
		{
			image.sprite = BgTypePattern[(int)bgType];
		}
	}
}
