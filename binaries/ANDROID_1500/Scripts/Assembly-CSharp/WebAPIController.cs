using System;
using System.Collections;
using Firebase.Messaging;
using UnityEngine;
using UnityEngine.Networking;

public class WebAPIController : MonoBehaviour
{
	public enum ClientVersion
	{
		Undefine = 0,
		Ver_01_00_00 = 1000,
		Ver_01_00_01 = 1001,
		Ver_01_01_00 = 1100,
		Ver_01_02_00 = 1200,
		Ver_01_03_00 = 1300,
		Ver_01_04_00 = 1400,
		Ver_01_05_00 = 1500,
		LastVerPlus = 1501,
		CurrentVer = 1500
	}

	public class ApiTokenResult
	{
		public string access_token;

		public long expires_in;
	}

	public static WebAPIController Instance;

	private string _Host = string.Empty;

	private string _ApiToken;

	public string Host => _Host;

	public string UserID { get; set; }

	public string LoginOnetimeToken { get; set; }

	public string ApiToken => _ApiToken;

	public WebAPIController()
	{
		if (Instance == null)
		{
			Instance = this;
		}
	}

	private void Start()
	{
		FirebaseMessaging.TokenReceived += OnTokenReceived;
		FirebaseMessaging.MessageReceived += OnMessageReceived;
	}

	public void OnTokenReceived(object sender, TokenReceivedEventArgs token)
	{
		Debug.Log("Received Registration Token: " + token.Token);
	}

	public void OnMessageReceived(object sender, MessageReceivedEventArgs e)
	{
		Debug.Log("Received a new message from: " + e.Message.From);
	}

	public void SetHost(string host)
	{
		Debug.Log("SetHost : " + host);
		_Host = host;
	}

	public void InitializeHost()
	{
		_Host = "https://companion.dd-on.jp";
	}

	public void SetAPIToken(string token)
	{
		_ApiToken = "Bearer " + token;
	}

	public void ClearApiToken()
	{
		_ApiToken = string.Empty;
		PlayerPerfManager.SetApiToken(string.Empty);
	}

	public static IEnumerator RequestApiToken(uint characterID, string oneTimeToken, Action onResult)
	{
		WWWForm form = new WWWForm();
		form.AddField("token", oneTimeToken);
		form.AddField("character", characterID.ToString());
		form.AddField("uuid", PlayerPerfManager.GetUUID());
		form.AddField("os", SystemInfo.operatingSystem);
		form.AddField("device", SystemInfo.deviceModel);
		form.AddField("clver", 1500.ToString());
		form.AddField("platform", 1);
		UnityWebRequest request = UnityWebRequest.Post(Instance.Host + "/token", form);
		yield return request.Send();
		if (!string.IsNullOrEmpty(request.error))
		{
			Debug.Log(request.error);
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			Instance.ServerConnectionError();
			yield break;
		}
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			ApiTokenResult apiTokenResult = JsonUtility.FromJson<ApiTokenResult>(text);
			Instance._ApiToken = "Bearer " + apiTokenResult.access_token;
			PlayerPerfManager.SetApiToken(apiTokenResult.access_token);
			onResult();
			yield break;
		}
		SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		if (request.responseCode < 0)
		{
			Instance.ServerConnectionError();
			yield break;
		}
		SingletonMonoBehaviour<ModalDialog>.Instance.Error(ModalDialog.Mode.OK, "エラー", request.downloadHandler.text, delegate
		{
			NavigationViewController.ResetScene();
		});
	}

	public void ServerConnectionError()
	{
		SingletonMonoBehaviour<ModalDialog>.Instance.Error(ModalDialog.Mode.OK, "接続エラー", "サーバーへの接続に失敗しました。タイトルへ戻ります。", delegate
		{
			NavigationViewController.ResetScene();
		});
	}

	public bool HandleError(UnityWebRequest request, Action<UnityWebRequest> customError, string apiName)
	{
		if (request.responseCode == 401)
		{
			string text = request.downloadHandler.text;
			if (string.IsNullOrEmpty(text))
			{
				text = "再ログインが必要なため、\nタイトルに戻ります";
			}
			SingletonMonoBehaviour<ModalDialog>.Instance.Error(ModalDialog.Mode.OK, "確認", text, delegate
			{
				Instance.ClearApiToken();
				NavigationViewController.ResetScene();
			});
			return true;
		}
		if (request.responseCode == 502)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Error(ModalDialog.Mode.OK, "接続エラー", "サーバーへの接続が失敗しました。タイトルへ戻ります。\ncode:" + request.responseCode, delegate
			{
				NavigationViewController.ResetScene();
			});
			return true;
		}
		if (request.responseCode == 503)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Error(ModalDialog.Mode.OK, "メンテナンス", request.downloadHandler.text, delegate
			{
				NavigationViewController.ResetScene();
			});
			return true;
		}
		if (request.responseCode == 404)
		{
			if (!(SingletonMonoBehaviour<NavigationViewController>.Instance == null) && SingletonMonoBehaviour<NavigationViewController>.Instance.StackCount != 0)
			{
				SingletonMonoBehaviour<ModalDialog>.Instance.Error(ModalDialog.Mode.OK, "利用不可", request.downloadHandler.text, delegate
				{
					SingletonMonoBehaviour<NavigationViewController>.Instance.AllPop();
				});
			}
			return true;
		}
		if (request.responseCode > 401 && request.responseCode < 500)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Error(ModalDialog.Mode.OK, "クライアントエラー", "エラーが発生しました。タイトルへ戻ります。\ncode:" + request.responseCode, delegate
			{
				NavigationViewController.ResetScene();
			});
			return true;
		}
		if (request.responseCode >= 500 && request.responseCode < 600)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Error(ModalDialog.Mode.OK, "サーバーエラー", "エラーが発生しました。タイトルへ戻ります。\ncode:" + request.responseCode, delegate
			{
				NavigationViewController.ResetScene();
			});
			return true;
		}
		if (request.responseCode < 0)
		{
			ServerConnectionError();
			return true;
		}
		string text2 = request.downloadHandler.text;
		if (string.IsNullOrEmpty(text2))
		{
			text2 = "エラーが発生しました。";
		}
		Debug.LogError("WebRequest code:" + request.responseCode + "\n" + text2);
		if (customError != null)
		{
			customError(request);
		}
		else
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Error(ModalDialog.Mode.OK, "リクエストエラー", text2 + "\ncode:" + request.responseCode, delegate
			{
			});
			if (SingletonMonoBehaviour<NavigationViewController>.Instance != null)
			{
				SingletonMonoBehaviour<NavigationViewController>.Instance.AllPop();
			}
		}
		return false;
	}
}
