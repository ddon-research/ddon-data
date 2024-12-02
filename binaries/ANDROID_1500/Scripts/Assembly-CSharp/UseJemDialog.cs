using System;
using UnityEngine;
using UnityEngine.UI;

public class UseJemDialog : SingletonMonoBehaviour<UseJemDialog>
{
	private CanvasGroup CachedCanvasGroup;

	[SerializeField]
	private GameObject Dialog;

	[SerializeField]
	private Button Button1;

	[SerializeField]
	private Button Button2;

	[SerializeField]
	private Text BodyText;

	[SerializeField]
	private Text BeforeJem;

	[SerializeField]
	private Text AfterJem;

	[SerializeField]
	private float FadeTime = 0.1f;

	private void Start()
	{
		CachedCanvasGroup = Dialog.gameObject.GetComponent<CanvasGroup>();
		CachedCanvasGroup.interactable = false;
		NavigationViewController.AddProhibit(Dialog);
	}

	public void Show(string itemName, uint price, Action<bool> OnResult = null)
	{
		if (SingletonMonoBehaviour<ChargeManager>.Instance.GetToralJem() < price)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "黄金石のカケラが不足しています", delegate
			{
				OnResult(obj: false);
			});
			return;
		}
		CachedCanvasGroup.alpha = 0f;
		CachedCanvasGroup.FadeTo(1f, FadeTime, 0f, iTween.EaseType.easeOutSine, delegate
		{
			CachedCanvasGroup.interactable = true;
		});
		Dialog.SetActive(value: true);
		BodyText.text = itemName + "の際に<color=#EFFFA5FF>黄金石のカケラ</color>が\n" + price + "個必要です。よろしいですか？";
		long toralJem = SingletonMonoBehaviour<ChargeManager>.Instance.GetToralJem();
		BeforeJem.text = toralJem.ToString("N0");
		if (toralJem > price)
		{
			AfterJem.text = (toralJem - price).ToString("N0");
		}
		else
		{
			AfterJem.text = "0";
		}
		Button1.onClick.RemoveAllListeners();
		Button2.onClick.RemoveAllListeners();
		Button1.gameObject.SetActive(value: true);
		Button1.onClick.AddListener(delegate
		{
			OnPressButton(OnResult, result: true);
		});
		Button2.gameObject.SetActive(value: true);
		Button2.onClick.AddListener(delegate
		{
			OnPressButton(OnResult, result: false);
		});
	}

	private void OnPressButton(Action<bool> OnResult, bool result)
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
