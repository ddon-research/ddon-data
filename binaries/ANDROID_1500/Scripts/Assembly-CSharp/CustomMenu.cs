using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;

public class CustomMenu : MonoBehaviour, ICustomMenu
{
	[SerializeField]
	private GameObject Baloon;

	[SerializeField]
	private CanvasGroup ContentCanvas;

	[SerializeField]
	private GameObject Box;

	[SerializeField]
	private GameObject Content;

	[SerializeField]
	private GameObject ContentPrefab;

	[SerializeField]
	private GameObject BorderPrefab;

	[SerializeField]
	private float AnimTime = 0.5f;

	[SerializeField]
	private bool _IsChanging;

	[SerializeField]
	private float AnimX = 0.1f;

	[SerializeField]
	private float AnimY = 0.1f;

	[SerializeField]
	private float FadeOutTime = 0.2f;

	[SerializeField]
	private float ContentFadeInTime = 0.2f;

	[SerializeField]
	private float ContentFadeDelayTime = 0.2f;

	[SerializeField]
	private AutoLayoutRebuilder BaloonRebuilder;

	[SerializeField]
	private BlackFadeController MyBlackFade;

	public bool IsChanging
	{
		get
		{
			return _IsChanging;
		}
		set
		{
			_IsChanging = value;
		}
	}

	private void Awake()
	{
		NavigationViewController.AddProhibit(Box);
	}

	private void Start()
	{
		BaloonRebuilder.MarkRebuild();
	}

	public void OnClick()
	{
		if (!IsChanging)
		{
			if (Baloon.activeInHierarchy)
			{
				OnDeactivate();
			}
			else
			{
				OnActivate();
			}
		}
	}

	public void Deactivate()
	{
		if (Baloon.activeInHierarchy && !IsChanging)
		{
			OnDeactivate();
		}
	}

	private void OnActivate()
	{
		IsChanging = true;
		Baloon.SetActive(value: true);
		RectTransform boxRect = Baloon.transform as RectTransform;
		boxRect.ScaleFrom(new Vector2
		{
			x = AnimX,
			y = AnimY
		}, AnimTime, 0f, iTween.EaseType.easeInSine);
		ContentCanvas.alpha = 0f;
		ContentCanvas.FadeTo(1f, ContentFadeInTime, ContentFadeDelayTime, iTween.EaseType.easeInSine, delegate
		{
			iTween.Stop(boxRect.gameObject);
			IsChanging = false;
		});
		MyBlackFade = SingletonMonoBehaviour<AppUtility>.Instance.ShowBlackout(base.gameObject.transform.parent, base.transform.GetSiblingIndex(), delegate
		{
			Deactivate();
		});
	}

	public bool IsMenuEmpty()
	{
		if (Content.transform.childCount == 0)
		{
			return true;
		}
		return false;
	}

	private void OnDeactivate()
	{
		IsChanging = true;
		GameObject clone = Object.Instantiate(Baloon);
		clone.transform.SetParent(Baloon.transform.parent);
		clone.transform.position = Baloon.transform.position;
		clone.transform.localScale = new Vector3(1f, 1f, 1f);
		AutoLayoutRebuilder component = clone.GetComponent<AutoLayoutRebuilder>();
		component.MarkRebuild();
		CanvasGroup component2 = clone.GetComponent<CanvasGroup>();
		component2.FadeTo(0f, FadeOutTime, 0f, iTween.EaseType.easeOutSine, delegate
		{
			iTween.Stop(clone);
			Object.Destroy(clone);
			IsChanging = false;
			if (EventSystem.current != null)
			{
				EventSystem.current.SetSelectedGameObject(null);
			}
		}, delegate
		{
			if (Baloon.activeInHierarchy)
			{
				Baloon.SetActive(value: false);
			}
		});
		if (MyBlackFade != null)
		{
			MyBlackFade.CloseBlackout();
			MyBlackFade = null;
		}
	}

	public void SetContent(List<CustomMenuContentData> elements)
	{
		ClearContent();
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
				GameObject gameObject2 = Object.Instantiate(ContentPrefab);
				gameObject2.transform.parent = Content.transform;
				gameObject2.transform.localScale = new Vector3(1f, 1f, 1f);
				CustomMenuContent component = gameObject2.GetComponent<CustomMenuContent>();
				component.UpdateContent(this, element);
			}
		}
		BaloonRebuilder.MarkRebuild();
	}

	public void ClearContent()
	{
		foreach (Transform componentInChild in Content.transform.GetComponentInChildren<Transform>())
		{
			Object.Destroy(componentInChild.gameObject);
		}
	}
}
