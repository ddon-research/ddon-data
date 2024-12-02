using System;
using UnityEngine;

public class FadeController : SingletonMonoBehaviour<FadeController>
{
	[SerializeField]
	private CanvasGroup FadeCanvas;

	[SerializeField]
	private float FadeSecond = 1f;

	public void FadeIn(Action OnFadeEnd)
	{
		FadeCanvas.alpha = 0f;
		FadeCanvas.gameObject.SetActive(value: true);
		FadeCanvas.FadeTo(1f, FadeSecond, 0f, iTween.EaseType.linear, delegate
		{
			OnFadeEnd();
		});
	}

	public void FadeOut(Action OnFadeEnd)
	{
		FadeCanvas.alpha = 1f;
		FadeCanvas.gameObject.SetActive(value: true);
		FadeCanvas.FadeTo(0f, FadeSecond, 0f, iTween.EaseType.linear, delegate
		{
			OnFadeEnd();
			FadeCanvas.gameObject.SetActive(value: false);
		});
	}
}
