using System.Collections;
using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementSubReward : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private Image OtherIcon;

	[SerializeField]
	private ItemIcon ItemIcon;

	[SerializeField]
	private Image Frame;

	[SerializeField]
	private Image FrameEx;

	[SerializeField]
	private Image SpotBoss;

	private IEnumerator routine;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
		Frame.gameObject.SetActive(value: false);
		FrameEx.gameObject.SetActive(value: false);
		SpotBoss.gameObject.SetActive(value: false);
		if ((DispParam.Param2 & 1) != 0)
		{
			FrameEx.gameObject.SetActive(value: true);
		}
		else
		{
			Frame.gameObject.SetActive(value: true);
		}
		if ((DispParam.Param2 & 2) != 0)
		{
			SpotBoss.gameObject.SetActive(value: true);
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
		string filePath = "Images/info/detail/" + iconParam;
		routine = LoadManager.LoadAsync(filePath, delegate(Sprite res)
		{
			if (res == null)
			{
				ItemIcon.gameObject.SetActive(value: true);
				ItemIcon.Load(iconParam, colorId);
			}
			else
			{
				OtherIcon.sprite = res;
				OtherIcon.gameObject.SetActive(value: true);
			}
			routine = null;
		});
		if (base.gameObject.activeInHierarchy)
		{
			StartCoroutine(routine);
		}
	}
}
