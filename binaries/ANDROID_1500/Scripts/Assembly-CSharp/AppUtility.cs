using System;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.UI;

public class AppUtility : SingletonMonoBehaviour<AppUtility>
{
	[SerializeField]
	private GameObject BlackFadePrefab;

	[SerializeField]
	public float FadeTime;

	[SerializeField]
	public float NoticeTime;

	[SerializeField]
	public NoticeBar NoticeBar;

	[SerializeField]
	public CanvasGroup NoticeCanvasGroup;

	public Queue<NoticeBarContent> NoticeStack = new Queue<NoticeBarContent>();

	public static bool CheckSuccessAndPop(int result, int successCode, string packetName)
	{
		if (result != successCode)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "エラー", "エラーが発生しました。\n(" + packetName + ":" + result + ")", delegate(ModalDialog.Result res)
			{
				if (res == ModalDialog.Result.OK)
				{
					SingletonMonoBehaviour<NavigationViewController>.Instance.Pop();
				}
			});
			return false;
		}
		return true;
	}

	public static bool CheckErrorAndPop(int result, int errorCode, string message)
	{
		if (result == errorCode)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "エラー", message, delegate(ModalDialog.Result res)
			{
				if (res == ModalDialog.Result.OK)
				{
					SingletonMonoBehaviour<NavigationViewController>.Instance.Pop();
				}
			});
			return false;
		}
		return true;
	}

	public static void ShowErr(string text, string packetName, bool IsPop = true, Action Callback = null)
	{
		ErrorCodePacket errorCodePacket = ErrorPacketParse(text);
		string text2 = errorCodePacket.Message;
		if (text2.Length == 0)
		{
			text2 = "リクエストエラー\n" + packetName + "(code:" + errorCodePacket.ErrorCode + ")";
		}
		SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "エラー", text2, delegate(ModalDialog.Result res)
		{
			if (res == ModalDialog.Result.OK)
			{
				if (IsPop)
				{
					SingletonMonoBehaviour<NavigationViewController>.Instance.Pop();
				}
				if (Callback != null)
				{
					Callback();
				}
			}
		});
	}

	public void ShowDialogAndPop(string title, string message, Action onCallBack = null)
	{
		SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, title, message, delegate(ModalDialog.Result res)
		{
			if (res == ModalDialog.Result.OK)
			{
				if (onCallBack != null)
				{
					onCallBack();
				}
				SingletonMonoBehaviour<NavigationViewController>.Instance.PopCore();
			}
		});
	}

	public BlackFadeController ShowBlackout(Transform parent, int siblingIndex, Action onCallback = null)
	{
		GameObject gameObject = UnityEngine.Object.Instantiate(BlackFadePrefab);
		RectTransform component = gameObject.GetComponent<RectTransform>();
		Vector2 anchoredPosition = component.anchoredPosition - parent.GetComponent<RectTransform>().anchoredPosition;
		gameObject.transform.parent = parent;
		gameObject.transform.localScale = new Vector3(1f, 1f, 1f);
		gameObject.transform.SetSiblingIndex(siblingIndex);
		component.anchoredPosition = anchoredPosition;
		CanvasGroup component2 = gameObject.GetComponent<CanvasGroup>();
		BlackFadeController component3 = gameObject.GetComponent<BlackFadeController>();
		component2.alpha = 0f;
		gameObject.SetActive(value: true);
		component2.FadeTo(1f, FadeTime, 0f, iTween.EaseType.easeInSine);
		if (onCallback != null)
		{
			Button component4 = gameObject.GetComponent<Button>();
			component4.onClick.RemoveAllListeners();
			component4.onClick.AddListener(delegate
			{
				onCallback();
			});
		}
		return component3;
	}

	public static ErrorCodePacket ErrorPacketParse(string text)
	{
		return JsonUtility.FromJson<ErrorCodePacket>(text);
	}

	public void AddNotice(NoticeBarContent notice)
	{
	}

	private void Update()
	{
	}

	public void TestNotice()
	{
	}
}
