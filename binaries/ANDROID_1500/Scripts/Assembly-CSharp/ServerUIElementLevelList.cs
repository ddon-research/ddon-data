using System.Collections;
using Packet;
using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementLevelList : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private TextNumDataTable TextNumTable;

	[SerializeField]
	private GameObject LevelObejct;

	[SerializeField]
	private Button LabelButton;

	[SerializeField]
	private Image Arrow;

	private IEnumerator routine;

	[SerializeField]
	private Image MyImage;

	public override void SetupElement()
	{
		ulong num = DispParam.Param1;
		MyImage.gameObject.SetActive(value: false);
		if (num == 0)
		{
			GameObject num2 = TextNumTable.GetNum(0u);
			GameObject gameObject = Object.Instantiate(num2);
			gameObject.transform.localScale = new Vector3(1f, 1f, 1f);
			gameObject.transform.SetParent(LevelObejct.transform);
		}
		else
		{
			while (num != 0)
			{
				ulong num3 = num % 10;
				GameObject num4 = TextNumTable.GetNum((uint)num3);
				GameObject gameObject2 = Object.Instantiate(num4);
				gameObject2.transform.SetParent(LevelObejct.transform);
				gameObject2.transform.localScale = new Vector3(1f, 1f, 1f);
				gameObject2.transform.SetSiblingIndex(0);
				num /= 10;
			}
		}
		Label.text = DispParam.Text1;
		if (DispParam.Text2.Length > 0)
		{
			LoadImageAsync(DispParam.Text2);
		}
		if (Link == LinkType.INVALID)
		{
			LabelButton.enabled = false;
			Arrow.enabled = false;
		}
		LayoutRebuilder.ForceRebuildLayoutImmediate(base.transform as RectTransform);
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
		MyImage.gameObject.SetActive(value: true);
		string filePath = "Images/info/detail/" + iconParam;
		routine = LoadManager.LoadAsync(filePath, delegate(Sprite res)
		{
			if (MyImage != null)
			{
				MyImage.sprite = res;
			}
			routine = null;
		});
		if (base.gameObject.activeInHierarchy)
		{
			StartCoroutine(routine);
		}
	}
}
