using System;
using System.Collections;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.Networking;

namespace WebRequest;

public class Charge
{
	private static Dictionary<string, CacheValue<CharacterJemList>> Cache_GetJemList = new Dictionary<string, CacheValue<CharacterJemList>>();

	private static Dictionary<string, CacheValue<JemInfo>> Cache_GetJemInfo = new Dictionary<string, CacheValue<JemInfo>>();

	public static IEnumerator GetJemList(Action<CharacterJemList> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetJemList.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/charge/jem_list");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterJemList characterJemList = JsonUtility.FromJson<CharacterJemList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CharacterJemList> cacheValue = new CacheValue<CharacterJemList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = characterJemList;
				Cache_GetJemList[cacheKey] = cacheValue;
			}
			onResult(characterJemList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/charge/jem_list");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetJemList()
	{
		Cache_GetJemList.Clear();
	}

	public static IEnumerator GetJemInfo(Action<JemInfo> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetJemInfo.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/charge/jem_info");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			JemInfo jemInfo = JsonUtility.FromJson<JemInfo>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<JemInfo> cacheValue = new CacheValue<JemInfo>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = jemInfo;
				Cache_GetJemInfo[cacheKey] = cacheValue;
			}
			onResult(jemInfo);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/charge/jem_info");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetJemInfo()
	{
		Cache_GetJemInfo.Clear();
	}

	public static void ClearCache()
	{
		Cache_GetJemList.Clear();
		Cache_GetJemInfo.Clear();
	}
}
