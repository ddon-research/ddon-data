using System;
using UnityEngine;

public static class iTweenUIExtensions
{
	private static iTweenEventHandler SetUpEventHandler(GameObject targetObj)
	{
		iTweenEventHandler iTweenEventHandler2 = targetObj.GetComponent<iTweenEventHandler>();
		if (iTweenEventHandler2 == null)
		{
			iTweenEventHandler2 = targetObj.AddComponent<iTweenEventHandler>();
		}
		return iTweenEventHandler2;
	}

	public static void MoveTo(this RectTransform target, Vector2 pos, float time, float delay, iTween.EaseType easeType, Action onCompleteDelegate = null)
	{
		iTweenEventHandler iTweenEventHandler2 = SetUpEventHandler(target.gameObject);
		iTweenEventHandler2.OnUpdateMoveDelegate = delegate(Vector2 value)
		{
			target.anchoredPosition = value;
		};
		iTweenEventHandler2.OnCompleteDelegate[iTweenEventHandler.ANIMATION_TYPE.MOVE_TO] = onCompleteDelegate;
		iTween.ValueTo(target.gameObject, iTween.Hash("from", target.anchoredPosition, "to", pos, "time", time, "delay", delay, "easetype", easeType, "onupdate", "OnUpdateMove", "onupdatetarget", iTweenEventHandler2.gameObject, "oncomplete", "OnComplete", "oncompletetarget", iTweenEventHandler2.gameObject, "oncompleteparams", iTweenEventHandler.ANIMATION_TYPE.MOVE_TO));
	}

	public static void FadeTo(this CanvasGroup target, float alpha, float time, float delay, iTween.EaseType easeType, Action onCompleteDelegate = null, Action onUpdateDelegate = null)
	{
		iTweenEventHandler iTweenEventHandler2 = SetUpEventHandler(target.gameObject);
		iTweenEventHandler2.OnUpdateAlphaDelegate = delegate(float value)
		{
			target.alpha = value;
			if (onUpdateDelegate != null)
			{
				onUpdateDelegate();
			}
		};
		iTweenEventHandler2.OnCompleteDelegate[iTweenEventHandler.ANIMATION_TYPE.FADE_TO] = onCompleteDelegate;
		iTween.ValueTo(target.gameObject, iTween.Hash("from", target.alpha, "to", alpha, "time", time, "delay", delay, "easetype", easeType, "onupdate", "OnUpdateAlpha", "onupdatetarget", iTweenEventHandler2.gameObject, "oncomplete", "OnComplete", "oncompletetarget", iTweenEventHandler2.gameObject, "oncompleteparams", iTweenEventHandler.ANIMATION_TYPE.FADE_TO));
	}

	public static void FadeFrom(this CanvasGroup target, float alpha, float time, float delay, iTween.EaseType easeType, Action onCompleteDelegate = null)
	{
		iTweenEventHandler iTweenEventHandler2 = SetUpEventHandler(target.gameObject);
		iTweenEventHandler2.OnUpdateAlphaDelegate = delegate(float value)
		{
			target.alpha = value;
		};
		iTweenEventHandler2.OnCompleteDelegate[iTweenEventHandler.ANIMATION_TYPE.FADE_FROM] = onCompleteDelegate;
		iTween.ValueTo(target.gameObject, iTween.Hash("from", alpha, "to", target.alpha, "time", time, "delay", delay, "easetype", easeType, "onupdate", "OnUpdateAlpha", "onupdatetarget", iTweenEventHandler2.gameObject, "oncomplete", "OnComplete", "oncompletetarget", iTweenEventHandler2.gameObject, "oncompleteparams", iTweenEventHandler.ANIMATION_TYPE.FADE_FROM));
	}

	public static void ScaleFrom(this RectTransform target, Vector2 pos, float time, float delay, iTween.EaseType easeType, Action onCompleteDelegate = null)
	{
		iTweenEventHandler iTweenEventHandler2 = SetUpEventHandler(target.gameObject);
		iTweenEventHandler2.OnCompleteDelegate[iTweenEventHandler.ANIMATION_TYPE.SCALE_FROM] = onCompleteDelegate;
		iTween.ScaleFrom(target.gameObject, iTween.Hash("x", pos.x, "y", pos.y, "time", time, "delay", delay, "easetype", easeType, "oncomplete", "OnComplete", "oncompletetarget", iTweenEventHandler2.gameObject, "oncompleteparams", iTweenEventHandler.ANIMATION_TYPE.SCALE_FROM));
	}

	public static void ScaleTo(this RectTransform target, Vector2 pos, float time, float delay, iTween.EaseType easeType, Action onCompleteDelegate = null)
	{
		iTweenEventHandler iTweenEventHandler2 = SetUpEventHandler(target.gameObject);
		iTweenEventHandler2.OnCompleteDelegate[iTweenEventHandler.ANIMATION_TYPE.SCALE_TO] = onCompleteDelegate;
		iTween.ScaleTo(target.gameObject, iTween.Hash("x", pos.x, "y", pos.y, "time", time, "delay", delay, "easetype", easeType, "oncomplete", "OnComplete", "oncompletetarget", iTweenEventHandler2.gameObject, "oncompleteparams", iTweenEventHandler.ANIMATION_TYPE.SCALE_TO));
	}

	public static void PunchPosition(this RectTransform target, Vector2 pos, float time, float delay, iTween.EaseType easeType, Action onCompleteDelegate = null)
	{
		iTweenEventHandler iTweenEventHandler2 = SetUpEventHandler(target.gameObject);
		iTweenEventHandler2.OnCompleteDelegate[iTweenEventHandler.ANIMATION_TYPE.PUNCH_POS] = onCompleteDelegate;
		iTween.PunchPosition(target.gameObject, iTween.Hash("x", pos.x, "y", pos.y, "time", time, "delay", delay, "easetype", easeType, "oncomplete", "OnComplete", "oncompletetarget", iTweenEventHandler2.gameObject, "oncompleteparams", iTweenEventHandler.ANIMATION_TYPE.PUNCH_POS));
	}
}
