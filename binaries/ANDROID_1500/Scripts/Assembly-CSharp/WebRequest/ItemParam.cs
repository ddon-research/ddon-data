using System;
using System.Collections;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.Networking;

namespace WebRequest;

public class ItemParam
{
	private static Dictionary<string, CacheValue<ItemData>> Cache_GetUInt32 = new Dictionary<string, CacheValue<ItemData>>();

	private static Dictionary<string, CacheValue<ItemDataList>> Cache_GetWeaponRefineItems = new Dictionary<string, CacheValue<ItemDataList>>();

	private static Dictionary<string, CacheValue<ItemDataList>> Cache_GetProtecterRefineItems = new Dictionary<string, CacheValue<ItemDataList>>();

	public static IEnumerator Get(Action<ItemData> onResult, Action<UnityWebRequest> onError, uint id, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + id;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetUInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/ItemParam" + "?id=" + id);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			ItemData itemData = JsonUtility.FromJson<ItemData>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<ItemData> cacheValue = new CacheValue<ItemData>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = itemData;
				Cache_GetUInt32[cacheKey] = cacheValue;
			}
			onResult(itemData);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/ItemParam");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetUInt32()
	{
		Cache_GetUInt32.Clear();
	}

	public static IEnumerator GetWeaponRefineItems(Action<ItemDataList> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetWeaponRefineItems.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/ItemParam/weapon_refine_items");
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			ItemDataList itemDataList = JsonUtility.FromJson<ItemDataList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<ItemDataList> cacheValue = new CacheValue<ItemDataList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = itemDataList;
				Cache_GetWeaponRefineItems[cacheKey] = cacheValue;
			}
			onResult(itemDataList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/ItemParam/weapon_refine_items");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetWeaponRefineItems()
	{
		Cache_GetWeaponRefineItems.Clear();
	}

	public static IEnumerator GetProtecterRefineItems(Action<ItemDataList> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetProtecterRefineItems.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/ItemParam/protecter_refine_items");
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			ItemDataList itemDataList = JsonUtility.FromJson<ItemDataList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<ItemDataList> cacheValue = new CacheValue<ItemDataList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = itemDataList;
				Cache_GetProtecterRefineItems[cacheKey] = cacheValue;
			}
			onResult(itemDataList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/ItemParam/protecter_refine_items");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetProtecterRefineItems()
	{
		Cache_GetProtecterRefineItems.Clear();
	}

	public static void ClearCache()
	{
		Cache_GetUInt32.Clear();
		Cache_GetWeaponRefineItems.Clear();
		Cache_GetProtecterRefineItems.Clear();
	}
}
