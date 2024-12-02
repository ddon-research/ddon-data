using System;
using System.Collections;
using Packet;
using UnityEngine;
using UnityEngine.Networking;

namespace WebRequest;

public class LoginBonus
{
	public static IEnumerator PostCheckDailyBonus(Action<CharacterDailyBonusList> onResult, Action<UnityWebRequest> onError, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + "/api/login_bonus/check_daily_bonus";
		request.downloadHandler = new DownloadHandlerBuffer();
		request.SetRequestHeader("Content-Type", "application/json");
		request.SetRequestHeader("charset", "UTF=8");
		request.method = "POST";
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterDailyBonusList obj = JsonUtility.FromJson<CharacterDailyBonusList>(text);
			onResult(obj);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/login_bonus/check_daily_bonus");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static IEnumerator PostResetDailyBonusDebug(Action onResult, Action<UnityWebRequest> onError, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + "/api/login_bonus/reset_daily_bonus_debug";
		request.downloadHandler = new DownloadHandlerBuffer();
		request.SetRequestHeader("Content-Type", "application/json");
		request.SetRequestHeader("charset", "UTF=8");
		request.method = "POST";
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			_ = request.downloadHandler.text;
			onResult();
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/login_bonus/reset_daily_bonus_debug");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache()
	{
	}
}
