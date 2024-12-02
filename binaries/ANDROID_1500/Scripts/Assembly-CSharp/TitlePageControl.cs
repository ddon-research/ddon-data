using System;
using System.Collections;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.Analytics;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using WebRequest;

public class TitlePageControl : ViewController
{
	[Serializable]
	public class UrlMap
	{
		[Serializable]
		public class KeyValue
		{
			public int Key;

			public string Value;

			public KeyValue(int key, string value)
			{
				Key = key;
				Value = value;
			}
		}

		public List<KeyValue> MapDataList;
	}

	[SerializeField]
	private DialogBox IntoroductionView;

	[SerializeField]
	private DialogBox TosView;

	[SerializeField]
	private Text VersionText;

	private EventSystem EventSystem;

	[SerializeField]
	private ViewController LoginView;

	[SerializeField]
	private MainViewController MainPage;

	private ClientVersionCheckResultPacket VersionResult;

	private const string SerialCode = "ddonl_an-20181009-0039";

	private uint ClickCapcomNum;

	[SerializeField]
	private Button DebugLoginButton;

	[SerializeField]
	private ViewController DebugLoginView;

	private void Awake()
	{
		EventSystem = UnityEngine.Object.FindObjectOfType<EventSystem>();
		SingletonMonoBehaviour<FadeController>.Instance.FadeOut(delegate
		{
		});
		VersionText.text = "01.05.00";
	}

	private void Start()
	{
		Input.multiTouchEnabled = false;
	}

	public void OnClickLogin()
	{
		WebAPIController.Instance.InitializeHost();
		WebRequest.CacheManager.ClearAll();
		if (!PlayerPerfManager.GetIsReadTitleIntroduction())
		{
			IntoroductionView.Show(DialogBox.Mode.Button1_Button2, string.Empty, string.Empty, delegate(DialogBox.Result res)
			{
				if (res != DialogBox.Result.Button1)
				{
					PlayerPerfManager.SetIsReadTitleIntroduction(b: true);
					CheckVersion();
				}
			});
		}
		else
		{
			CheckVersion();
		}
	}

	public void CheckVersion()
	{
		ClientVersionCheckPacket clientVersionCheckPacket = new ClientVersionCheckPacket();
		clientVersionCheckPacket.ClientVersion = 1500u;
		clientVersionCheckPacket.PlatformID = Packet.PlatformID.ANDROID;
		StartCoroutine(ClientVersionCheck.PostCheckVersion(delegate(ClientVersionCheckResultPacket res)
		{
			VersionResult = res;
			if (!VersionResult.IsOk)
			{
				SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "最新バージョンへの更新が必要です", delegate
				{
					WebAPIController.Instance.ClearApiToken();
					Application.OpenURL(res.StoreUrl);
				});
			}
			else
			{
				WebAPIController.Instance.SetHost(res.Url);
				StartCoroutine(CheckTOS());
			}
		}, null, clientVersionCheckPacket, LoadingAnimation.Default));
	}

	private IEnumerator CheckTOS()
	{
		yield return null;
		int read = PlayerPerfManager.GetReadTosVersion();
		if (VersionResult.TosVersion > read)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
			yield return TOSController.LoadTos(VersionResult.TosUrl, delegate(string text)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
				TosView.Show(DialogBox.Mode.Button1_Button2, string.Empty, text, delegate(DialogBox.Result res)
				{
					if (res != DialogBox.Result.Button1)
					{
						PlayerPerfManager.SetReadTosVersion((int)VersionResult.TosVersion);
						ShowLoginPage();
					}
				});
			}, delegate(string errText)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
				SingletonMonoBehaviour<ModalDialog>.Instance.Error(ModalDialog.Mode.OK, "エラー", errText, delegate
				{
					ShowLoginPage();
				});
			});
		}
		else
		{
			ShowLoginPage();
		}
	}

	private void ShowLoginPage()
	{
		string apiToken = PlayerPerfManager.GetApiToken();
		if (!string.IsNullOrEmpty(apiToken))
		{
			WebAPIController.Instance.SetAPIToken(apiToken);
			Debug.Log("Set API Token");
			StartCoroutine(CharacterData.GetBase(delegate(CharacterDataBase data)
			{
				Debug.Log("GetBase");
				SingletonMonoBehaviour<ProfileManager>.Instance.SetCharacterData(data);
				SingletonMonoBehaviour<ChargeManager>.Instance.SetJem(data.Jem);
				MainPage.SetFirstLoading();
				MainPage.CachedCanvasGroup.alpha = 0f;
				MainPage.gameObject.SetActive(value: true);
				MainPage.SetCharacterData(data);
				MainPage.CachedCanvasGroup.FadeTo(1f, 0.5f, 0.1f, iTween.EaseType.easeOutSine, delegate
				{
					base.gameObject.SetActive(value: false);
					base.CachedCanvasGroup.blocksRaycasts = true;
				});
			}, null, null, LoadingAnimation.Default));
		}
		else
		{
			base.CachedCanvasGroup.blocksRaycasts = false;
			LoginView.gameObject.SetActive(value: true);
			Vector2 anchoredPosition = LoginView.CachedRectTransform.anchoredPosition;
			LoginView.CachedRectTransform.anchoredPosition = new Vector2(anchoredPosition.x, 0f - base.CachedRectTransform.rect.height);
			LoginView.CachedRectTransform.MoveTo(new Vector2(0f, 0f), 0.3f, 0f, iTween.EaseType.easeOutCubic, delegate
			{
				base.CachedCanvasGroup.blocksRaycasts = true;
			});
		}
	}

	public void OpenOfficalSite()
	{
		Analytics.CustomEvent("ClickToOpenOfficalSiteOnTitlePage");
		Application.OpenURL("https://members.dd-on.jp/");
	}

	public void OnClickCapcom()
	{
	}

	public void OnClickDebugLogin()
	{
	}
}
