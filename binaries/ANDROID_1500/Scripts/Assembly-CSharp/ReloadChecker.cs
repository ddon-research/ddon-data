using System;
using UnityEngine;
using UnityEngine.UI;

public class ReloadChecker : MonoBehaviour
{
	[SerializeField]
	private RectTransform ReloadButton;

	[SerializeField]
	private ScrollRect TargetScrollRect;

	[SerializeField]
	private bool IsHide;

	[SerializeField]
	private float MoveTime = 0.5f;

	private float MoveDistance = 200f;

	private Vector2 OriginPos;

	private Vector2 HidePos;

	[SerializeField]
	private bool IsInit;

	private Action Callback;

	[SerializeField]
	private bool IsAnimating;

	[SerializeField]
	private bool CanClikable = true;

	[SerializeField]
	private bool CanShow;

	private void Start()
	{
	}

	public void Init(Action callback = null)
	{
		if (!IsInit)
		{
			MoveDistance = ReloadButton.sizeDelta.y * 3f;
			Callback = callback;
			OriginPos = ReloadButton.anchoredPosition;
			HidePos = OriginPos + new Vector2(0f, MoveDistance);
			IsInit = true;
		}
		PosInit();
	}

	public void PosInit()
	{
		iTween.Stop(ReloadButton.gameObject);
		ReloadButton.anchoredPosition = HidePos;
		IsHide = false;
		IsAnimating = false;
		CanClikable = true;
		CanShow = false;
		Hide();
	}

	public void OnEnable()
	{
		PosInit();
	}

	private void Update()
	{
		if (TargetScrollRect.velocity.y > 0f)
		{
			Hide();
		}
		else if (TargetScrollRect.velocity.y < 0f && CanShow)
		{
			Show();
		}
	}

	private void Show()
	{
		if (!IsAnimating && IsHide)
		{
			IsAnimating = true;
			ReloadButton.MoveTo(OriginPos, MoveTime, 0f, iTween.EaseType.easeInSine, delegate
			{
				IsAnimating = false;
				IsHide = false;
			});
		}
	}

	private void Hide()
	{
		if (!IsAnimating && !IsHide)
		{
			IsAnimating = true;
			ReloadButton.MoveTo(HidePos, MoveTime, 0f, iTween.EaseType.easeOutSine, delegate
			{
				IsAnimating = false;
				IsHide = true;
				CanClikable = true;
			});
		}
	}

	public void OnClick()
	{
		if (Callback != null)
		{
			CanClikable = false;
			CanShow = false;
			Hide();
			Callback();
		}
	}

	public void MarkShowReload()
	{
		bool canShow = CanShow;
		CanShow = true;
		if (!canShow)
		{
			Show();
		}
	}

	public void MarkHideReload()
	{
		CanShow = false;
		Hide();
	}
}
