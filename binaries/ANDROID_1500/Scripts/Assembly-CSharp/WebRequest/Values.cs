using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using Packet;
using UnityEngine;
using UnityEngine.Networking;

namespace WebRequest;

public class Values
{
	private static Dictionary<string, CacheValue<string>> Cache_Get = new Dictionary<string, CacheValue<string>>();

	private static Dictionary<string, CacheValue<string>> Cache_GetInt32Int32 = new Dictionary<string, CacheValue<string>>();

	private static Dictionary<string, CacheValue<string>> Cache_GetManyInt32Int32Int32Int32 = new Dictionary<string, CacheValue<string>>();

	public static IEnumerator Get(Action<string> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/values");
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
				Cache_Get[cacheKey] = cacheValue;
			}
			onResult(text2);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/values");
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

	public static IEnumerator Get(Action<string> onResult, Action<UnityWebRequest> onError, int id, int no, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + id + "/" + no;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetInt32Int32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/values/{id}/{no}");
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
				Cache_GetInt32Int32[cacheKey] = cacheValue;
			}
			onResult(text2);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/values/{id}/{no}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetInt32Int32()
	{
		Cache_GetInt32Int32.Clear();
	}

	public static IEnumerator GetMany(Action<string> onResult, Action<UnityWebRequest> onError, int id, int no, int type, int count, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + id + "/" + no + "/" + type + "/" + count;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetManyInt32Int32Int32Int32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/values/many/{id}/{no}" + "?type=" + type + "&count=" + count);
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
				Cache_GetManyInt32Int32Int32Int32[cacheKey] = cacheValue;
			}
			onResult(text2);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/values/many/{id}/{no}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetManyInt32Int32Int32Int32()
	{
		Cache_GetManyInt32Int32Int32Int32.Clear();
	}

	public static IEnumerator Post(Action onResult, Action<UnityWebRequest> onError, string value, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + "/api/values";
		string json2 = string.Empty;
		json2 = json2 + "\"" + value + "\"";
		byte[] bodyRaw = Encoding.UTF8.GetBytes(json2);
		request.uploadHandler = new UploadHandlerRaw(bodyRaw);
		request.downloadHandler = new DownloadHandlerBuffer();
		request.SetRequestHeader("Content-Type", "application/json");
		request.SetRequestHeader("charset", "UTF=8");
		request.method = "POST";
		yield return request.Send();
		if (request.responseCode == 200)
		{
			_ = request.downloadHandler.text;
			onResult();
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/values");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static IEnumerator Put(Action onResult, Action<UnityWebRequest> onError, int id, int no, UraguchiInput value, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + $"/api/values/{id}" + "?no=" + no;
		string json2 = string.Empty;
		json2 += JsonUtility.ToJson(value);
		byte[] bodyRaw = Encoding.UTF8.GetBytes(json2);
		request.uploadHandler = new UploadHandlerRaw(bodyRaw);
		request.downloadHandler = new DownloadHandlerBuffer();
		request.SetRequestHeader("Content-Type", "application/json");
		request.SetRequestHeader("charset", "UTF=8");
		request.method = "PUT";
		yield return request.Send();
		if (request.responseCode == 200)
		{
			_ = request.downloadHandler.text;
			onResult();
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/values/{id}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static IEnumerator Delete(Action onResult, Action<UnityWebRequest> onError, int id, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = UnityWebRequest.Delete(WebAPIController.Instance.Host + $"/api/values/{id}");
		request.downloadHandler = new DownloadHandlerBuffer();
		yield return request.Send();
		if (request.responseCode == 200)
		{
			_ = request.downloadHandler.text;
			onResult();
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/values/{id}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache()
	{
		Cache_Get.Clear();
		Cache_GetInt32Int32.Clear();
		Cache_GetManyInt32Int32Int32Int32.Clear();
	}
}
