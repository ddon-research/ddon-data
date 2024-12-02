using System;
using System.Collections.Generic;
using Frame;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

[RequireComponent(typeof(CanvasGroup))]
public class NavigationViewController : SingletonMonoBehaviour<NavigationViewController>
{
	public enum NavigationDir
	{
		Forward,
		Back
	}

	public enum Direction
	{
		None,
		Left,
		Right,
		Top,
		Buttom
	}

	private EventSystem EventSystem;

	private Stack<ViewController> stackedViews = new Stack<ViewController>();

	private ViewController currentView;

	[SerializeField]
	private ViewController basePage;

	[SerializeField]
	private Text titleLabel;

	[SerializeField]
	private Button backButton;

	private bool ShowQuitDaialogue;

	private static HashSet<GameObject> ProhibitPageBackList = new HashSet<GameObject>();

	public float MoveTime = 0.3f;

	public float MoveDelay;

	public iTween.EaseType MoveEaseType = iTween.EaseType.easeOutSine;

	[SerializeField]
	private TopFrameController TopFrame;

	[SerializeField]
	private ViewController OptionBase;

	[SerializeField]
	private ViewController FullScreenOptionBase;

	[SerializeField]
	private GameObject NavigationButtons;

	private ViewController ObjectOnOptionBase;

	[SerializeField]
	private NavigationViewHeader NavHeader;

	[SerializeField]
	private NavigationViewHeader FullScreenNavHeader;

	private Vector2 DefaultNaviHeaderPos;

	private Vector2 FullScreenNaviHeaderPos;

	public NavigationDir PrevNavigationDir { get; set; }

	public int StackCount => stackedViews.Count;

	public static void AddProhibit(GameObject obj)
	{
		ProhibitPageBackList.Add(obj);
	}

	public void AllPop()
	{
		SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		while (stackedViews.Count > 0)
		{
			PopCore();
		}
	}

	public bool IfHasStackPop(Action onCallBack = null)
	{
		if (stackedViews.Count > 0)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK_Cancel, "確認", "このページから離れます。\nよろしいですか？", delegate(ModalDialog.Result res)
			{
				if (res == ModalDialog.Result.OK)
				{
					AllPop();
					if (onCallBack != null)
					{
						onCallBack();
					}
				}
			});
			return true;
		}
		return false;
	}

	private new void Awake()
	{
		EventSystem = UnityEngine.Object.FindObjectOfType<EventSystem>();
		if (backButton != null)
		{
			backButton.onClick.AddListener(OnPressBackButton);
		}
		OptionBase.gameObject.SetActive(value: false);
		FullScreenOptionBase.gameObject.SetActive(value: false);
	}

	private void OnEnable()
	{
		stackedViews.Clear();
		currentView = null;
		Push(basePage);
	}

	public void OnPressBackButton()
	{
		Pop();
	}

	private void EnableInteraction(bool isEnabled)
	{
		if (EventSystem == null)
		{
			EventSystem = UnityEngine.Object.FindObjectOfType<EventSystem>();
		}
		EventSystem.enabled = isEnabled;
	}

	public void PushIfNull(ViewController newView)
	{
		if (currentView == null)
		{
			Push(newView);
		}
	}

	public void Push(ViewController newView)
	{
		Push(newView, newView.MoveDirection, MoveTime, MoveDelay, MoveEaseType);
	}

	public void Push(ViewController newView, Direction dir, float time, float delay, iTween.EaseType easeType)
	{
		if (currentView == null)
		{
			newView.gameObject.SetActive(value: true);
			currentView = newView;
			return;
		}
		PrevNavigationDir = NavigationDir.Forward;
		EnableInteraction(isEnabled: false);
		ViewController lastView = currentView;
		if (!lastView.IsFullScreen)
		{
			stackedViews.Push(lastView);
			if (newView.IsFullScreen)
			{
				dir = Direction.Top;
			}
		}
		else if (lastView as ServerUIBase != null)
		{
			stackedViews.Push(lastView);
			if (newView.IsFullScreen)
			{
				dir = Direction.Top;
			}
		}
		if (lastView.Option != null)
		{
			lastView.Option.gameObject.SetActive(value: false);
		}
		lastView.CachedCanvasGroup.FadeTo(0f, time, delay, iTween.EaseType.easeOutSine, delegate
		{
			lastView.gameObject.SetActive(value: false);
		});
		Action action = delegate
		{
			EnableInteraction(isEnabled: true);
			newView.OnNavigationPushEnd();
		};
		Vector2 anchoredPosition = newView.CachedRectTransform.anchoredPosition;
		newView.gameObject.SetActive(value: true);
		newView.CachedCanvasGroup.alpha = 1f;
		switch (dir)
		{
		case Direction.None:
			anchoredPosition = newView.CachedRectTransform.anchoredPosition;
			anchoredPosition.x = 0f;
			anchoredPosition.y = 0f;
			newView.CachedRectTransform.anchoredPosition = anchoredPosition;
			newView.CachedCanvasGroup.alpha = 0f;
			newView.CachedCanvasGroup.FadeTo(1f, time, delay, iTween.EaseType.easeOutSine, delegate
			{
				EnableInteraction(isEnabled: true);
				lastView.gameObject.SetActive(value: false);
			});
			break;
		case Direction.Left:
			newView.CachedRectTransform.anchoredPosition = new Vector2(0f - newView.CachedRectTransform.rect.width, anchoredPosition.y);
			anchoredPosition.x = 0f;
			newView.CachedRectTransform.MoveTo(anchoredPosition, time, delay, easeType, delegate
			{
				EnableInteraction(isEnabled: true);
				newView.OnNavigationPushEnd();
			});
			break;
		case Direction.Right:
			newView.CachedRectTransform.anchoredPosition = new Vector2(newView.CachedRectTransform.rect.width, anchoredPosition.y);
			anchoredPosition.x = 0f;
			newView.CachedRectTransform.MoveTo(anchoredPosition, time, delay, easeType, delegate
			{
				EnableInteraction(isEnabled: true);
				newView.OnNavigationPushEnd();
			});
			break;
		case Direction.Top:
			newView.CachedRectTransform.anchoredPosition = new Vector2(anchoredPosition.x, newView.CachedRectTransform.rect.height);
			anchoredPosition.y = 0f;
			newView.CachedRectTransform.MoveTo(anchoredPosition, time, delay, easeType, delegate
			{
				EnableInteraction(isEnabled: true);
				newView.OnNavigationPushEnd();
			});
			break;
		case Direction.Buttom:
			newView.CachedRectTransform.anchoredPosition = new Vector2(anchoredPosition.x, 0f - newView.CachedRectTransform.rect.height);
			anchoredPosition.y = 0f;
			newView.CachedRectTransform.MoveTo(anchoredPosition, time, delay, easeType, delegate
			{
				EnableInteraction(isEnabled: true);
				newView.OnNavigationPushEnd();
			});
			break;
		}
		currentView = newView;
		SetHeaderContent(newView);
		backButton.gameObject.SetActive(value: true);
	}

	public void Pop()
	{
		if (currentView.IsPopBeginCheck)
		{
			string text = currentView.PopBeginCheckMessage;
			if (text.Length == 0)
			{
				text = "このページから離れます。\nよろしいですか？";
			}
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK_Cancel, "確認", text, delegate(ModalDialog.Result result)
			{
				if (result == ModalDialog.Result.OK)
				{
					PopCore();
				}
			});
		}
		else
		{
			PopCore();
		}
	}

	public void PopCore()
	{
		uint popCount = currentView.PopCount;
		if (popCount > 1)
		{
			for (int i = 0; i < popCount; i++)
			{
				Pop(i != popCount - 1);
			}
		}
		else
		{
			Pop(null);
		}
	}

	public void Pop(bool cantActive)
	{
		Pop(null, cantActive);
	}

	public void Pop(ViewController view, bool cantActive = false)
	{
		if (stackedViews.Count < 1 || (view != null && stackedViews.Peek() != view))
		{
			return;
		}
		PrevNavigationDir = NavigationDir.Back;
		EnableInteraction(isEnabled: false);
		currentView.OnNavigationPopBegin();
		ViewController lastView = currentView;
		Vector2 anchoredPosition = lastView.CachedRectTransform.anchoredPosition;
		Direction direction = lastView.MoveDirection;
		if (lastView.Option != null)
		{
			lastView.Option.gameObject.SetActive(value: false);
		}
		if (lastView.IsFullScreen)
		{
			direction = Direction.Top;
		}
		switch (direction)
		{
		case Direction.None:
			lastView.CachedCanvasGroup.alpha = 1f;
			lastView.CachedCanvasGroup.FadeTo(0f, 0.3f, 0f, iTween.EaseType.easeOutSine, delegate
			{
				lastView.gameObject.SetActive(value: false);
				if (lastView.GetComponent<ServerUIBase>() != null)
				{
					UnityEngine.Object.Destroy(lastView.gameObject);
				}
			});
			break;
		case Direction.Left:
			anchoredPosition.x = 0f - lastView.CachedRectTransform.rect.width;
			lastView.CachedRectTransform.MoveTo(anchoredPosition, MoveTime, MoveDelay, MoveEaseType, delegate
			{
				lastView.gameObject.SetActive(value: false);
				if (lastView.GetComponent<ServerUIBase>() != null)
				{
					UnityEngine.Object.Destroy(lastView.gameObject);
				}
			});
			break;
		case Direction.Right:
			anchoredPosition.x = lastView.CachedRectTransform.rect.width;
			lastView.CachedRectTransform.MoveTo(anchoredPosition, MoveTime, MoveDelay, MoveEaseType, delegate
			{
				lastView.gameObject.SetActive(value: false);
				if (lastView.GetComponent<ServerUIBase>() != null)
				{
					UnityEngine.Object.Destroy(lastView.gameObject);
				}
			});
			break;
		case Direction.Top:
			anchoredPosition.y = lastView.CachedRectTransform.rect.height;
			lastView.CachedRectTransform.MoveTo(anchoredPosition, MoveTime, MoveDelay, MoveEaseType, delegate
			{
				lastView.gameObject.SetActive(value: false);
				if (lastView.GetComponent<ServerUIBase>() != null)
				{
					UnityEngine.Object.Destroy(lastView.gameObject);
				}
			});
			break;
		case Direction.Buttom:
			anchoredPosition.y = 0f - lastView.CachedRectTransform.rect.height;
			lastView.CachedRectTransform.MoveTo(anchoredPosition, MoveTime, MoveDelay, MoveEaseType, delegate
			{
				lastView.gameObject.SetActive(value: false);
				if (lastView.GetComponent<ServerUIBase>() != null)
				{
					UnityEngine.Object.Destroy(lastView.gameObject);
				}
			});
			break;
		}
		ViewController viewController = stackedViews.Pop();
		if (!cantActive)
		{
			viewController.gameObject.SetActive(value: true);
		}
		viewController.CachedCanvasGroup.FadeTo(1f, 0.3f, 0f, iTween.EaseType.easeOutSine, delegate
		{
			EnableInteraction(isEnabled: true);
		});
		currentView = viewController;
		SetHeaderContent(viewController);
	}

	private void SetHeaderContent(ViewController view)
	{
		if (stackedViews.Count > 0)
		{
			NavHeader.gameObject.SetActive(value: false);
			FullScreenNavHeader.gameObject.SetActive(value: false);
			if (view.IsFullScreen)
			{
				FullScreenNavHeader.gameObject.SetActive(view.UseNaviHeader);
				TopFrame.gameObject.SetActive(value: false);
				FullScreenOptionBase.gameObject.SetActive(value: true);
				OptionBase.gameObject.SetActive(value: false);
				NavigationButtons.SetActive(value: false);
			}
			else
			{
				NavHeader.gameObject.SetActive(view.UseNaviHeader);
				TopFrame.gameObject.SetActive(value: true);
				FullScreenOptionBase.gameObject.SetActive(value: false);
				OptionBase.gameObject.SetActive(value: true);
				NavigationButtons.SetActive(value: true);
			}
			if (view.Option != null)
			{
				view.Option.gameObject.SetActive(value: true);
				ViewController option = view.Option;
				Vector3 localScale = option.transform.localScale;
				Vector2 sizeDelta = option.CachedRectTransform.sizeDelta;
				Vector2 offsetMin = option.CachedRectTransform.offsetMin;
				Vector2 offsetMax = option.CachedRectTransform.offsetMax;
				if (view.IsFullScreen)
				{
					option.transform.SetParent(FullScreenOptionBase.transform);
				}
				else
				{
					option.transform.SetParent(OptionBase.transform);
				}
				option.transform.localScale = localScale;
				option.CachedRectTransform.sizeDelta = sizeDelta;
				option.CachedRectTransform.offsetMin = offsetMin;
				option.CachedRectTransform.offsetMax = offsetMax;
			}
		}
		else
		{
			TopFrame.gameObject.SetActive(value: true);
			NavHeader.gameObject.SetActive(value: false);
			FullScreenNavHeader.gameObject.SetActive(value: false);
			FullScreenOptionBase.gameObject.SetActive(value: false);
			OptionBase.gameObject.SetActive(value: false);
			NavigationButtons.SetActive(value: true);
		}
		NavHeader.UpdateContents(view);
		FullScreenNavHeader.UpdateContents(view);
	}

	public void ProhibitListClear()
	{
		ProhibitPageBackList.Clear();
	}

	public void Update()
	{
		if (!Input.GetKeyDown(KeyCode.Escape) || SingletonMonoBehaviour<ModalDialog>.Instance.IsShow)
		{
			return;
		}
		foreach (GameObject prohibitPageBack in ProhibitPageBackList)
		{
			if (prohibitPageBack.activeInHierarchy)
			{
				return;
			}
		}
		if (StackCount == 0)
		{
			if (ShowQuitDaialogue)
			{
				return;
			}
			ShowQuitDaialogue = true;
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK_Cancel, "アプリケーション終了確認", "Dragon's Dogma Online 冒険手帳\nを終了しますか？", delegate(ModalDialog.Result res)
			{
				ShowQuitDaialogue = false;
				if (res == ModalDialog.Result.OK)
				{
					Application.Quit();
				}
			});
		}
		Pop();
	}

	public static void ResetScene()
	{
		if (SingletonMonoBehaviour<NavigationViewController>.Instance != null)
		{
			SingletonMonoBehaviour<NavigationViewController>.Instance.ProhibitListClear();
		}
		SceneManager.LoadScene("Main");
	}
}
