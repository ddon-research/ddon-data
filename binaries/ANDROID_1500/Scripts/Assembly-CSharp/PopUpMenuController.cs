using System.Collections.Generic;
using UnityEngine;

public class PopUpMenuController : SingletonMonoBehaviour<PopUpMenuController>, ICustomMenu
{
	[SerializeField]
	private CanvasGroup Background;

	[SerializeField]
	private GameObject MenuButtonPrefab;

	[SerializeField]
	private GameObject BorderPrefab;

	[SerializeField]
	private GameObject Content;

	[SerializeField]
	private float FadeAnimTime;

	public bool IsChanging { get; set; }

	public bool IsUsing => Background.gameObject.activeInHierarchy;

	public void Start()
	{
		NavigationViewController.AddProhibit(Background.gameObject);
	}

	public void Show(List<CustomMenuContentData> listData)
	{
		if (IsUsing)
		{
			Debug.Log("他がポップアップメニュー使用している");
			return;
		}
		ClearMenu();
		NavigationViewController.AddProhibit(Background.gameObject);
		IsChanging = true;
		Background.alpha = 0f;
		Background.gameObject.SetActive(value: true);
		SetContent(listData);
		Background.FadeTo(1f, FadeAnimTime, 0f, iTween.EaseType.easeInSine, delegate
		{
			IsChanging = false;
		});
	}

	private void ClearMenu()
	{
		foreach (Transform componentInChild in Content.transform.GetComponentInChildren<Transform>())
		{
			Object.Destroy(componentInChild.gameObject);
		}
	}

	public void SetContent(List<CustomMenuContentData> elements)
	{
		foreach (CustomMenuContentData element in elements)
		{
			if (element.IsBorder)
			{
				GameObject gameObject = Object.Instantiate(BorderPrefab);
				gameObject.transform.parent = Content.transform;
				gameObject.transform.localScale = new Vector3(1f, 1f, 1f);
			}
			else
			{
				GameObject gameObject2 = Object.Instantiate(MenuButtonPrefab);
				gameObject2.transform.parent = Content.transform;
				gameObject2.transform.localScale = new Vector3(1f, 1f, 1f);
				CustomMenuContent component = gameObject2.GetComponent<CustomMenuContent>();
				component.UpdateContent(this, element);
			}
		}
	}

	public void Deactivate()
	{
		if (!IsChanging)
		{
			IsChanging = true;
			Background.FadeTo(0f, FadeAnimTime, 0f, iTween.EaseType.easeOutSine, delegate
			{
				IsChanging = false;
				ClearMenu();
				Background.gameObject.SetActive(value: false);
			});
		}
	}
}
