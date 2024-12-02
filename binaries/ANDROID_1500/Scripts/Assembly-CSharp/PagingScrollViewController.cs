using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;

[RequireComponent(typeof(ScrollRect))]
public class PagingScrollViewController : ViewController
{
	public class OnPageMovedEvent : UnityEvent<int>
	{
	}

	[SerializeField]
	private PageControl pageControl;

	private Rect currentViewRect;

	private ScrollRect cachedScrollRect;

	private bool isAnimating;

	private Vector2 destPosition;

	private Vector2 initialPosition;

	private AnimationCurve animationCurve;

	private int prevPageIndex;

	[SerializeField]
	public OnPageMovedEvent OnPageMoved = new OnPageMovedEvent();

	[SerializeField]
	private List<PagingScrollViewButton> ViewButtons = new List<PagingScrollViewButton>();

	[SerializeField]
	private bool IsHomePage;

	public ScrollRect CachedScrollRect
	{
		get
		{
			if (cachedScrollRect == null)
			{
				cachedScrollRect = GetComponent<ScrollRect>();
			}
			return cachedScrollRect;
		}
	}

	private void Start()
	{
		UpdateView();
		SetPage(1);
	}

	private void Update()
	{
		if (base.CachedRectTransform.rect.width != currentViewRect.width || base.CachedRectTransform.rect.height != currentViewRect.height)
		{
			UpdateView();
		}
	}

	public void MovePage(int pageIndex)
	{
		if (!SingletonMonoBehaviour<NavigationViewController>.Instance.IfHasStackPop(delegate
		{
			MovePage(pageIndex);
		}) && pageIndex != prevPageIndex)
		{
			float num = (float)pageIndex * base.CachedRectTransform.rect.width;
			destPosition = new Vector2(0f - num, CachedScrollRect.content.anchoredPosition.y);
			initialPosition = CachedScrollRect.content.anchoredPosition;
			Keyframe keyframe = new Keyframe(Time.time, 0f, 0f, 1f);
			Keyframe keyframe2 = new Keyframe(Time.time + 0.3f, 1f, 0f, 0f);
			animationCurve = new AnimationCurve(keyframe, keyframe2);
			isAnimating = true;
			pageControl.SetCurrentPage(pageIndex);
			ViewButtons[pageIndex].SetHightlightImageEnable(isEnable: true);
			ViewButtons[prevPageIndex].SetHightlightImageEnable(isEnable: false);
			prevPageIndex = pageIndex;
			if (OnPageMoved != null)
			{
				OnPageMoved.Invoke(pageIndex);
			}
		}
	}

	public void SetPage(int pageIndex)
	{
		float num = (float)pageIndex * base.CachedRectTransform.rect.width;
		destPosition = new Vector2(0f - num, CachedScrollRect.content.anchoredPosition.y);
		CachedScrollRect.content.anchoredPosition = destPosition;
		pageControl.SetCurrentPage(pageIndex);
		ViewButtons[pageIndex].SetHightlightImageEnable(isEnable: true);
		ViewButtons[prevPageIndex].SetHightlightImageEnable(isEnable: false);
		prevPageIndex = pageIndex;
	}

	private void LateUpdate()
	{
		if (!isAnimating)
		{
			return;
		}
		if (Time.time > animationCurve.keys[animationCurve.length - 1].time)
		{
			if (IsHomePage && prevPageIndex == 0)
			{
				SingletonMonoBehaviour<TutorialManager>.Instance.StartTutorial(TutorialManager.TutorialType.TUTORIAL_CALENDAR);
			}
			CachedScrollRect.content.anchoredPosition = destPosition;
			isAnimating = false;
		}
		else
		{
			Vector2 anchoredPosition = initialPosition + (destPosition - initialPosition) * animationCurve.Evaluate(Time.time);
			CachedScrollRect.content.anchoredPosition = anchoredPosition;
		}
	}

	private void UpdateView()
	{
		currentViewRect = base.CachedRectTransform.rect;
	}

	public void OnScrollHandler(Vector2 vec)
	{
		Debug.Log($"x={vec.x}, y={vec.y}");
	}
}
