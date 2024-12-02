using System;
using System.Collections;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.Networking;

namespace WebRequest;

public class Gift
{
	private static Dictionary<string, CacheValue<CharacterGiftList>> Cache_GetGiftList = new Dictionary<string, CacheValue<CharacterGiftList>>();

	public static IEnumerator GetGiftList(Action<CharacterGiftList> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetGiftList.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/gift/gift_list");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterGiftList characterGiftList = JsonUtility.FromJson<CharacterGiftList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CharacterGiftList> cacheValue = new CacheValue<CharacterGiftList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = characterGiftList;
				Cache_GetGiftList[cacheKey] = cacheValue;
			}
			onResult(characterGiftList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/gift/gift_list");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetGiftList()
	{
		Cache_GetGiftList.Clear();
	}

	public static IEnumerator PostReceiveGift(Action<ReceiveGift> onResult, Action<UnityWebRequest> onError, uint Id, Packet.PlatformID PlatformId, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + $"/api/gift/gift_receive/{Id}/{PlatformId}";
		request.downloadHandler = new DownloadHandlerBuffer();
		request.SetRequestHeader("Content-Type", "application/json");
		request.SetRequestHeader("charset", "UTF=8");
		request.method = "POST";
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			ReceiveGift obj = JsonUtility.FromJson<ReceiveGift>(text);
			onResult(obj);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/gift/gift_receive/{Id}/{PlatformId}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static IEnumerator PostReceiveGiftAll(Action<ReceiveGift> onResult, Action<UnityWebRequest> onError, Packet.PlatformID PlatformId, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + $"/api/gift/gift_receive_all/{PlatformId}";
		request.downloadHandler = new DownloadHandlerBuffer();
		request.SetRequestHeader("Content-Type", "application/json");
		request.SetRequestHeader("charset", "UTF=8");
		request.method = "POST";
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			ReceiveGift obj = JsonUtility.FromJson<ReceiveGift>(text);
			onResult(obj);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/gift/gift_receive_all/{PlatformId}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache()
	{
		Cache_GetGiftList.Clear();
	}
}
