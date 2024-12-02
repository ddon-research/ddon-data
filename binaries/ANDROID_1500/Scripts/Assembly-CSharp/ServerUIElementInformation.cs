using System.Collections;
using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementInformation : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private Image Icon;

	private IEnumerator routine;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
		LayoutRebuilder.ForceRebuildLayoutImmediate(Label.transform as RectTransform);
		LayoutRebuilder.ForceRebuildLayoutImmediate(base.transform as RectTransform);
		LoadImageAsync(DispParam.Text2);
	}

	private void OnEnable()
	{
		if (routine != null)
		{
			StartCoroutine(routine);
		}
	}

	public void LoadImageAsync(string iconParam)
	{
		string filePath = "Images/info/detail/" + iconParam;
		routine = LoadManager.LoadAsync(filePath, delegate(Sprite res)
		{
			if (Icon != null)
			{
				Icon.sprite = res;
			}
			routine = null;
		});
		if (base.gameObject.activeInHierarchy)
		{
			StartCoroutine(routine);
		}
	}
}
