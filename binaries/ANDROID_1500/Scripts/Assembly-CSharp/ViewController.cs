using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;

[RequireComponent(typeof(RectTransform))]
[RequireComponent(typeof(CanvasGroup))]
public class ViewController : MonoBehaviour
{
	private RectTransform cachedRectTransform;

	private CanvasGroup cachedCanvasGroup;

	[SerializeField]
	protected Sprite BaseIcon;

	[SerializeField]
	protected string BaseTitle;

	public uint PopCount = 1u;

	[SerializeField]
	public ViewController Option;

	[SerializeField]
	public bool IsFullScreen;

	[SerializeField]
	public bool UseNaviHeader = true;

	[SerializeField]
	public NavigationViewController.Direction MoveDirection = NavigationViewController.Direction.Right;

	[SerializeField]
	[Multiline]
	private string _PopBeginCheckMessage = string.Empty;

	[SerializeField]
	private bool _IsPopBeginCheck;

	[SerializeField]
	private UnityEvent OnPushEndCallback;

	[SerializeField]
	private UnityEvent OnPopBeginCallback;

	public RectTransform CachedRectTransform
	{
		get
		{
			if (cachedRectTransform == null)
			{
				cachedRectTransform = GetComponent<RectTransform>();
			}
			return cachedRectTransform;
		}
	}

	public CanvasGroup CachedCanvasGroup
	{
		get
		{
			if (cachedCanvasGroup == null)
			{
				cachedCanvasGroup = GetComponent<CanvasGroup>();
			}
			return cachedCanvasGroup;
		}
	}

	public virtual Sprite Icon => BaseIcon;

	public virtual string Title
	{
		get
		{
			return BaseTitle;
		}
		set
		{
			BaseTitle = value;
		}
	}

	public string PopBeginCheckMessage
	{
		get
		{
			return _PopBeginCheckMessage;
		}
		protected set
		{
			_PopBeginCheckMessage = value;
		}
	}

	public bool IsPopBeginCheck
	{
		get
		{
			return _IsPopBeginCheck;
		}
		protected set
		{
			_IsPopBeginCheck = value;
		}
	}

	public virtual void OnNavigationPushEnd()
	{
		OnPushEndCallback.Invoke();
	}

	public virtual void OnNavigationPopBegin()
	{
		OnPopBeginCallback.Invoke();
	}

	public virtual void Push()
	{
		SingletonMonoBehaviour<NavigationViewController>.Instance.Push(this);
	}

	public void ShowDialog(Toggle t)
	{
		ShowDialog(t.isOn);
	}

	public void ShowDialog(bool isShow)
	{
		if (isShow)
		{
			base.gameObject.SetActive(value: true);
			CachedCanvasGroup.FadeTo(1f, 0.15f, 0f, iTween.EaseType.easeOutSine, delegate
			{
			});
		}
		else
		{
			CachedCanvasGroup.FadeTo(0f, 0.15f, 0f, iTween.EaseType.easeOutSine, delegate
			{
				base.gameObject.SetActive(value: false);
			});
		}
	}

	public void SetPopBeginCheck(bool flag)
	{
		IsPopBeginCheck = flag;
	}
}
