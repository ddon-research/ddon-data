using System;
using System.Collections;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.Networking;

namespace WebRequest;

public class Environment
{
	private static Dictionary<string, CacheValue<Packet.Environment>> Cache_Get = new Dictionary<string, CacheValue<Packet.Environment>>();

	public static IEnumerator Get(Action<Packet.Environment> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_Get.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/environment");
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			Packet.Environment environment = JsonUtility.FromJson<Packet.Environment>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<Packet.Environment> cacheValue = new CacheValue<Packet.Environment>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = environment;
				Cache_Get[cacheKey] = cacheValue;
			}
			onResult(environment);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/environment");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_Get()
	{
		Cache_Get.Clear();
	}

	public static void ClearCache()
	{
		Cache_Get.Clear();
	}
}
