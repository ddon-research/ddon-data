using System.Collections;
using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementSearchInfo : ServerUIElementBase
{
	[SerializeField]
	private RectTransform Rect;

	[SerializeField]
	private Text Label;

	[SerializeField]
	private Text SubLabel;

	[SerializeField]
	private Image OtherIcon;

	[SerializeField]
	private ItemIcon ItemIcon;

	[SerializeField]
	private GameObject Extra;

	private IEnumerator routine;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
		if (DispParam.Param2 != 0)
		{
			Extra.SetActive(value: true);
			SubLabel.text = DispParam.Param2 + "以上";
			Rect.sizeDelta = new Vector2(Rect.sizeDelta.x, 140f);
		}
		if (DispParam.Text2 != string.Empty)
		{
			LoadImageAsync(DispParam.Text2, (uint)DispParam.Param1);
		}
		else
		{
			Label.rectTransform.sizeDelta = new Vector2(680f, Label.rectTransform.sizeDelta.y);
		}
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
