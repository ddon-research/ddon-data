using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using Packet;
using UnityEngine;
using UnityEngine.Networking;

namespace WebRequest;

public class COGCallback
{
	private static Dictionary<string, CacheValue<string>> Cache_GetString = new Dictionary<string, CacheValue<string>>();

	private static Dictionary<string, CacheValue<string>> Cache_GetInt32Int32 = new Dictionary<string, CacheValue<string>>();

	private static Dictionary<string, CacheValue<string>> Cache_GetManyInt32Int32Int32Int32 = new Dictionary<string, CacheValue<string>>();

	public static IEnumerator Get(Action<string> onResult, Action<UnityWebRequest> onError, string code, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + code;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetString.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/cog_callback" + "?code=" + code);
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
				Cache_GetString[cacheKey] = cacheValue;
			}
			onResult(text2);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/cog_callback");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetString()
	{
		Cache_GetString.Clear();
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
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/cog_callback" + "?id=" + id + "&no=" + no);
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
			WebAPIController.Instance.HandleError(request, onError, "api/cog_callback");
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
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/cog_callback/many/{id}/{no}" + "?type=" + type + "&count=" + count);
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
			WebAPIController.Instance.HandleError(request, onError, "api/cog_callback/many/{id}/{no}");
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

	public static IEnumerator Post(Action onResult, Action<UnityWebRequest> onError, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + "/api/cog_callback";
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
			WebAPIController.Instance.HandleError(request, onError, "api/cog_callback");
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
		request.url = WebAPIController.Instance.Host + "/api/cog_callback" + "?id=" + id + "&no=" + no;
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
			WebAPIController.Instance.HandleError(request, onError, "api/cog_callback");
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
		UnityWebRequest request = UnityWebRequest.Delete(WebAPIController.Instance.Host + "/api/cog_callback" + "?id=" + id);
		request.downloadHandler = new DownloadHandlerBuffer();
		yield return request.Send();
		if (request.responseCode == 200)
		{
			_ = request.downloadHandler.text;
			onResult();
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/cog_callback");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache()
	{
		Cache_GetString.Clear();
		Cache_GetInt32Int32.Clear();
		Cache_GetManyInt32Int32Int32Int32.Clear();
	}
}
