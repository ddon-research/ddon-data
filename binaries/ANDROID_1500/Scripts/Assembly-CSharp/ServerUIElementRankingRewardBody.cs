using System.Collections;
using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementRankingRewardBody : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private Text Num;

	[SerializeField]
	private Image OtherIcon;

	[SerializeField]
	private ItemIcon ItemIcon;

	private IEnumerator routine;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
		int num = (int)DispParam.Param2;
		if (num < 0)
		{
			Num.text = "在庫数\n∞";
		}
		else
		{
			Num.text = "在庫数\n" + DispParam.Param2;
		}
		LoadImageAsync(DispParam.Text2, (uint)DispParam.Param1);
	}

	private void OnEnable()
	{
		if (routine != null)
		{
			StartCoroutine(routine);
		}
	}

	public void LoadImageAsync(string iconParam, uint colorId)
	{
		OtherIcon.gameObject.SetActive(value: false);
		ItemIcon.gameObject.SetActive(value: false);
		if (colorId != 0)
		{
			ItemIcon.gameObject.SetActive(value: true);
			ItemIcon.Load(iconParam, colorId);
			return;
		}
		OtherIcon.gameObject.SetActive(value: true);
		string filePath = "Images/info/detail/" + iconParam;
		routine = LoadManager.LoadAsync(filePath, delegate(Sprite res)
		{
			if (OtherIcon != null)
			{
				OtherIcon.sprite = res;
			}
			routine = null;
		});
		if (base.gameObject.activeInHierarchy)
		{
			StartCoroutine(routine);
		}
	}
}
