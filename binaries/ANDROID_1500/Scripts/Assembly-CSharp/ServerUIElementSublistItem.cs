using System.Collections;
using Packet;
using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementSublistItem : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private Button LabelButton;

	[SerializeField]
	private Image Arrow;

	[SerializeField]
	private Image OtherIcon;

	[SerializeField]
	private ItemIcon ItemIcon;

	private IEnumerator routine;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
		if (Link == LinkType.INVALID)
		{
			LabelButton.enabled = false;
			Arrow.enabled = false;
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
