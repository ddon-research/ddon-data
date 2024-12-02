using System;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

public class ModalDialog : SingletonMonoBehaviour<ModalDialog>
{
	public enum Mode
	{
		OK,
		OK_Cancel,
		Yes_No,
		Button1_Button2
	}

	public enum Result
	{
		OK,
		Cancel,
		Yes,
		No,
		Button1,
		Button2
	}

	[SerializeField]
	private GameObject Dialog;

	[SerializeField]
	private Text TitleText;

	[SerializeField]
	private Text BodyText;

	[SerializeField]
	private Text ButtonText1;

	[SerializeField]
	private Text ButtonText2;

	[SerializeField]
	private Button Button1;

	[SerializeField]
	private Button Button2;

	private CanvasGroup CachedCanvasGroup;

	[SerializeField]
	private float FadeTime = 0.1f;

	private Color DefaultTextColor;

	[SerializeField]
	private Color ErrorTextColor = Color.red;

	public bool IsShow => Dialog.activeInHierarchy;

	private void Start()
	{
		CachedCanvasGroup = Dialog.gameObject.GetComponent<CanvasGroup>();
		CachedCanvasGroup.interactable = false;
		if (BodyText != null)
		{
			DefaultTextColor = BodyText.color;
		}
	}

	public void Show(Mode mode, string title, string body, Action<Result> OnResult = null)
	{
		UnityEngine.Object.FindObjectOfType<EventSystem>().enabled = true;
		if (BodyText != null)
		{
			BodyText.color = DefaultTextColor;
		}
		_show(mode, title, body, OnResult);
	}

	public void Error(Mode mode, string title, string body, Action<Result> OnResult = null)
	{
		UnityEngine.Object.FindObjectOfType<EventSystem>().enabled = true;
		if (BodyText != null)
		{
			BodyText.color = ErrorTextColor;
		}
		_show(mode, title, body, OnResult);
	}

	private void _show(Mode mode, string title, string body, Action<Result> OnResult = null)
	{
		CachedCanvasGroup.alpha = 0f;
		CachedCanvasGroup.FadeTo(1f, FadeTime, 0f, iTween.EaseType.easeOutSine, delegate
		{
			CachedCanvasGroup.interactable = true;
		});
		Dialog.SetActive(value: true);
		Button1.gameObject.SetActive(value: false);
		Button2.gameObject.SetActive(value: false);
		if (TitleText != null)
		{
			TitleText.text = title;
		}
		body = body.Replace("黄金石のカケラ", "<color=#EFFFA5FF>黄金石のカケラ</color>");
		if (BodyText != null)
		{
			BodyText.text = body;
		}
		Button1.onClick.RemoveAllListeners();
		Button2.onClick.RemoveAllListeners();
		switch (mode)
		{
		case Mode.OK:
			Button1.gameObject.SetActive(value: true);
			Button1.onClick.AddListener(delegate
			{
				OnPressButton(OnResult, Result.OK);
			});
			ButtonText1.text = "OK";
			break;
		case Mode.OK_Cancel:
			Button1.gameObject.SetActive(value: true);
			Button1.onClick.AddListener(delegate
			{
				OnPressButton(OnResult, Result.OK);
			});
			Button2.gameObject.SetActive(value: true);
			Button2.onClick.AddListener(delegate
			{
				OnPressButton(OnResult, Result.Cancel);
			});
			ButtonText1.text = "OK";
			ButtonText2.text = "キャンセル";
			break;
		case Mode.Yes_No:
			Button1.gameObject.SetActive(value: true);
			Button1.onClick.AddListener(delegate
			{
				OnPressButton(OnResult, Result.Yes);
			});
			Button2.gameObject.SetActive(value: true);
			Button2.onClick.AddListener(delegate
			{
				OnPressButton(OnResult, Result.No);
			});
			ButtonText1.text = "Yes";
			ButtonText2.text = "No";
			break;
		case Mode.Button1_Button2:
			Button1.gameObject.SetActive(value: true);
			Button1.onClick.AddListener(delegate
			{
				OnPressButton(OnResult, Result.Button1);
			});
			Button2.gameObject.SetActive(value: true);
			Button2.onClick.AddListener(delegate
			{
				OnPressButton(OnResult, Result.Button2);
			});
			break;
		}
	}

	private void OnPressButton(Action<Result> OnResult, Result result)
	{
		CachedCanvasGroup.interactable = false;
		CachedCanvasGroup.FadeTo(0f, FadeTime, 0f, iTween.EaseType.easeOutSine, delegate
		{
			Dialog.SetActive(value: false);
			if (OnResult != null)
			{
				OnResult(result);
			}
		});
	}
}
