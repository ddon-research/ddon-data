using System;
using System.Collections;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.Networking;

namespace WebRequest;

public class InGameURL
{
	private static Dictionary<string, CacheValue<string>> Cache_GetBanner = new Dictionary<string, CacheValue<string>>();

	private static Dictionary<string, CacheValue<string>> Cache_GetStaticResource = new Dictionary<string, CacheValue<string>>();

	private static Dictionary<string, CacheValue<TutorialPathList>> Cache_GetTutoriale = new Dictionary<string, CacheValue<TutorialPathList>>();

	public static IEnumerator GetBanner(Action<string> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetBanner.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/in_game_url/banner");
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			string text2 = text;
			if (!cacheOption.NoCache)
			{
				CacheValue<string> cacheValue = new CacheValue<string>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = text2;
				Cache_GetBanner[cacheKey] = cacheValue;
			}
			onResult(text2);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/in_game_url/banner");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetBanner()
	{
		Cache_GetBanner.Clear();
	}

	public static IEnumerator GetStaticResource(Action<string> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetStaticResource.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/in_game_url/StaticResource");
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			string text2 = text;
			if (!cacheOption.NoCache)
			{
				CacheValue<string> cacheValue = new CacheValue<string>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = text2;
				Cache_GetStaticResource[cacheKey] = cacheValue;
			}
			onResult(text2);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/in_game_url/StaticResource");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetStaticResource()
	{
		Cache_GetStaticResource.Clear();
	}

	public static IEnumerator GetTutoriale(Action<TutorialPathList> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetTutoriale.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/in_game_url/tutorial");
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			TutorialPathList tutorialPathList = JsonUtility.FromJson<TutorialPathList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<TutorialPathList> cacheValue = new CacheValue<TutorialPathList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = tutorialPathList;
				Cache_GetTutoriale[cacheKey] = cacheValue;
			}
			onResult(tutorialPathList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/in_game_url/tutorial");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetTutoriale()
	{
		Cache_GetTutoriale.Clear();
	}

	public static void ClearCache()
	{
		Cache_GetBanner.Clear();
		Cache_GetStaticResource.Clear();
		Cache_GetTutoriale.Clear();
	}
}
