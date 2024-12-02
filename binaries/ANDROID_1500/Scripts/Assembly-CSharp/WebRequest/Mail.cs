using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using Packet;
using UnityEngine;
using UnityEngine.Networking;

namespace WebRequest;

public class Mail
{
	private static Dictionary<string, CacheValue<MailReceivedList>> Cache_GetReceivedListMailType = new Dictionary<string, CacheValue<MailReceivedList>>();

	private static Dictionary<string, CacheValue<MailReceivedDetail>> Cache_GetReceivedDetailUInt64 = new Dictionary<string, CacheValue<MailReceivedDetail>>();

	private static Dictionary<string, CacheValue<MailSentList>> Cache_GetSentList = new Dictionary<string, CacheValue<MailSentList>>();

	private static Dictionary<string, CacheValue<MailSentDetail>> Cache_GetSentListUInt32 = new Dictionary<string, CacheValue<MailSentDetail>>();

	public static IEnumerator GetReceivedList(Action<MailReceivedList> onResult, Action<UnityWebRequest> onError, MailType mail_type, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + mail_type;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetReceivedListMailType.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/mail/received_list/{mail_type}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			MailReceivedList mailReceivedList = JsonUtility.FromJson<MailReceivedList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<MailReceivedList> cacheValue = new CacheValue<MailReceivedList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = mailReceivedList;
				Cache_GetReceivedListMailType[cacheKey] = cacheValue;
			}
			onResult(mailReceivedList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/mail/received_list/{mail_type}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetReceivedListMailType()
	{
		Cache_GetReceivedListMailType.Clear();
	}

	public static IEnumerator GetReceivedDetail(Action<MailReceivedDetail> onResult, Action<UnityWebRequest> onError, ulong id, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetReceivedDetailUInt64.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/mail/received_detail/{id}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			MailReceivedDetail mailReceivedDetail = JsonUtility.FromJson<MailReceivedDetail>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<MailReceivedDetail> cacheValue = new CacheValue<MailReceivedDetail>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = mailReceivedDetail;
				Cache_GetReceivedDetailUInt64[cacheKey] = cacheValue;
			}
			onResult(mailReceivedDetail);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/mail/received_detail/{id}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetReceivedDetailUInt64()
	{
		Cache_GetReceivedDetailUInt64.Clear();
	}

	public static IEnumerator GetSentList(Action<MailSentList> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetSentList.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/mail/sent_list");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			MailSentList mailSentList = JsonUtility.FromJson<MailSentList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<MailSentList> cacheValue = new CacheValue<MailSentList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = mailSentList;
				Cache_GetSentList[cacheKey] = cacheValue;
			}
			onResult(mailSentList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/mail/sent_list");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetSentList()
	{
		Cache_GetSentList.Clear();
	}

	public static IEnumerator GetSentList(Action<MailSentDetail> onResult, Action<UnityWebRequest> onError, uint id, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetSentListUInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/mail/sent_detail/{id}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			MailSentDetail mailSentDetail = JsonUtility.FromJson<MailSentDetail>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<MailSentDetail> cacheValue = new CacheValue<MailSentDetail>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = mailSentDetail;
				Cache_GetSentListUInt32[cacheKey] = cacheValue;
			}
			onResult(mailSentDetail);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/mail/sent_detail/{id}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetSentListUInt32()
	{
		Cache_GetSentListUInt32.Clear();
	}

	public static IEnumerator Post(Action<JemResult> onResult, Action<UnityWebRequest> onError, MailSendData data, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + "/api/mail/send_mail";
		string json2 = string.Empty;
		json2 += JsonUtility.ToJson(data);
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
			JemResult obj = JsonUtility.FromJson<JemResult>(text);
			onResult(obj);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/mail/send_mail");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache()
	{
		Cache_GetReceivedListMailType.Clear();
		Cache_GetReceivedDetailUInt64.Clear();
		Cache_GetSentList.Clear();
		Cache_GetSentListUInt32.Clear();
	}
}
