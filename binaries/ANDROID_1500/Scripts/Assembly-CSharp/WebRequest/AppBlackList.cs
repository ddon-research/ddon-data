using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using Packet;
using UnityEngine;
using UnityEngine.Networking;

namespace WebRequest;

public class AppBlackList
{
	private static Dictionary<string, CacheValue<AppBlackListParam>> Cache_GetList = new Dictionary<string, CacheValue<AppBlackListParam>>();

	public static IEnumerator GetList(Action<AppBlackListParam> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/";
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetList.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/AppBlackList/list");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			AppBlackListParam appBlackListParam = JsonUtility.FromJson<AppBlackListParam>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<AppBlackListParam> cacheValue = new CacheValue<AppBlackListParam>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = appBlackListParam;
				Cache_GetList[cacheKey] = cacheValue;
			}
			onResult(appBlackListParam);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/AppBlackList/list");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetList()
	{
		Cache_GetList.Clear();
	}

	public static IEnumerator PostList(Action<ErrorCodePacket> onResult, Action<UnityWebRequest> onError, AppBlackListParam valueParam, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + "/api/AppBlackList/list";
		string json2 = string.Empty;
		json2 += JsonUtility.ToJson(valueParam);
		byte[] bodyRaw = Encoding.UTF8.GetBytes(json2);
		request.uploadHandler = new UploadHandlerRaw(bodyRaw);
		request.downloadHandler = new DownloadHandlerBuffer();
		request.SetRequestHeader("Content-Type", "application/json");
		request.SetRequestHeader("charset", "UTF=8");
		request.method = "POST";
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			ErrorCodePacket obj = JsonUtility.FromJson<ErrorCodePacket>(text);
			onResult(obj);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/AppBlackList/list");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache()
	{
		Cache_GetList.Clear();
	}
}
