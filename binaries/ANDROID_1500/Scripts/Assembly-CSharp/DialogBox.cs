using System;
using UnityEngine;
using UnityEngine.UI;

public class DialogBox : ViewController
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

	public void Show(Mode mode, string title, string body, Action<Result> OnResult = null)
	{
		base.gameObject.SetActive(value: true);
		Button1.gameObject.SetActive(value: false);
		Button2.gameObject.SetActive(value: false);
		if (TitleText != null)
		{
			TitleText.text = title;
		}
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
		base.gameObject.SetActive(value: false);
		OnResult?.Invoke(result);
	}
}
