using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using Packet;
using UnityEngine;
using UnityEngine.Networking;

namespace WebRequest;

public class CharacterCalendar
{
	private static Dictionary<string, CacheValue<CalendarTopicParam>> Cache_GetTopicStringInt32Int32Int32Int32Int32 = new Dictionary<string, CacheValue<CalendarTopicParam>>();

	private static Dictionary<string, CacheValue<CalendarTopic>> Cache_GetSelectTopicInt32UInt64 = new Dictionary<string, CacheValue<CalendarTopic>>();

	private static Dictionary<string, CacheValue<CalendarAbstractParam>> Cache_GetAbstractInt32Int32 = new Dictionary<string, CacheValue<CalendarAbstractParam>>();

	private static Dictionary<string, CacheValue<CalendarUpdateInfoParam>> Cache_GetTopicUpdatedInfo = new Dictionary<string, CacheValue<CalendarUpdateInfoParam>>();

	private static Dictionary<string, CacheValue<TopicCommentParam>> Cache_GetCommentUInt64UInt32 = new Dictionary<string, CacheValue<TopicCommentParam>>();

	private static Dictionary<string, CacheValue<CalendarTopicParam>> Cache_GetBoardTopic = new Dictionary<string, CacheValue<CalendarTopicParam>>();

	public static IEnumerator GetTopic(Action<CalendarTopicParam> onResult, Action<UnityWebRequest> onError, string cmd, int type, int year, int month, int day, int param, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + cmd + "/" + type + "/" + year + "/" + month + "/" + day + "/" + param;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetTopicStringInt32Int32Int32Int32Int32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/CharacterCalendar/topic/{cmd}/{type}/{year}/{month}/{day}/{param}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CalendarTopicParam calendarTopicParam = JsonUtility.FromJson<CalendarTopicParam>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CalendarTopicParam> cacheValue = new CacheValue<CalendarTopicParam>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = calendarTopicParam;
				Cache_GetTopicStringInt32Int32Int32Int32Int32[cacheKey] = cacheValue;
			}
			onResult(calendarTopicParam);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterCalendar/topic/{cmd}/{type}/{year}/{month}/{day}/{param}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetTopicStringInt32Int32Int32Int32Int32()
	{
		Cache_GetTopicStringInt32Int32Int32Int32Int32.Clear();
	}

	public static IEnumerator GetSelectTopic(Action<CalendarTopic> onResult, Action<UnityWebRequest> onError, int type, ulong topicId, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + type + "/" + topicId;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetSelectTopicInt32UInt64.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/CharacterCalendar/topic/select/{type}/{topicId}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CalendarTopic calendarTopic = JsonUtility.FromJson<CalendarTopic>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CalendarTopic> cacheValue = new CacheValue<CalendarTopic>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = calendarTopic;
				Cache_GetSelectTopicInt32UInt64[cacheKey] = cacheValue;
			}
			onResult(calendarTopic);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterCalendar/topic/select/{type}/{topicId}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetSelectTopicInt32UInt64()
	{
		Cache_GetSelectTopicInt32UInt64.Clear();
	}

	public static IEnumerator GetAbstract(Action<CalendarAbstractParam> onResult, Action<UnityWebRequest> onError, int year, int month, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + year + "/" + month;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetAbstractInt32Int32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/CharacterCalendar/calendar/abstract/{year}/{month}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CalendarAbstractParam calendarAbstractParam = JsonUtility.FromJson<CalendarAbstractParam>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CalendarAbstractParam> cacheValue = new CacheValue<CalendarAbstractParam>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = calendarAbstractParam;
				Cache_GetAbstractInt32Int32[cacheKey] = cacheValue;
			}
			onResult(calendarAbstractParam);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterCalendar/calendar/abstract/{year}/{month}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetAbstractInt32Int32()
	{
		Cache_GetAbstractInt32Int32.Clear();
	}

	public static IEnumerator GetTopicUpdatedInfo(Action<CalendarUpdateInfoParam> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetTopicUpdatedInfo.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/CharacterCalendar/calendar/topiclist/updateinfo/");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CalendarUpdateInfoParam calendarUpdateInfoParam = JsonUtility.FromJson<CalendarUpdateInfoParam>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CalendarUpdateInfoParam> cacheValue = new CacheValue<CalendarUpdateInfoParam>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = calendarUpdateInfoParam;
				Cache_GetTopicUpdatedInfo[cacheKey] = cacheValue;
			}
			onResult(calendarUpdateInfoParam);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterCalendar/calendar/topiclist/updateinfo/");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetTopicUpdatedInfo()
	{
		Cache_GetTopicUpdatedInfo.Clear();
	}

	public static IEnumerator PostListUpdatedInfo(Action<CalendarUpdateInfoListParam> onResult, Action<UnityWebRequest> onError, CalendarUpdateInfo value, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + "/api/CharacterCalendar/calendar/topiclist/updateinfo/list/";
		string json2 = string.Empty;
		json2 += JsonUtility.ToJson(value);
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
			CalendarUpdateInfoListParam obj = JsonUtility.FromJson<CalendarUpdateInfoListParam>(text);
			onResult(obj);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterCalendar/calendar/topiclist/updateinfo/list/");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static IEnumerator GetComment(Action<TopicCommentParam> onResult, Action<UnityWebRequest> onError, ulong TopicId, uint offset, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + TopicId + "/" + offset;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetCommentUInt64UInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/CharacterCalendar/comment/{TopicId}/{offset}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			TopicCommentParam topicCommentParam = JsonUtility.FromJson<TopicCommentParam>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<TopicCommentParam> cacheValue = new CacheValue<TopicCommentParam>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = topicCommentParam;
				Cache_GetCommentUInt64UInt32[cacheKey] = cacheValue;
			}
			onResult(topicCommentParam);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterCalendar/comment/{TopicId}/{offset}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetCommentUInt64UInt32()
	{
		Cache_GetCommentUInt64UInt32.Clear();
	}

	public static IEnumerator PostTopic(Action<ErrorCodePacket> onResult, Action<UnityWebRequest> onError, string cmd, CalendarTopic value, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + $"/api/CharacterCalendar/topic/{cmd}";
		string json2 = string.Empty;
		json2 += JsonUtility.ToJson(value);
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
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterCalendar/topic/{cmd}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static IEnumerator PostComment(Action<ErrorCodePacket> onResult, Action<UnityWebRequest> onError, string cmd, TopicComment value, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + $"/api/CharacterCalendar/comment/{cmd}";
		string json2 = string.Empty;
		json2 += JsonUtility.ToJson(value);
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
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterCalendar/comment/{cmd}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static IEnumerator DeleteTopic(Action<ErrorCodePacket> onResult, Action<UnityWebRequest> onError, ulong calId, int type, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = UnityWebRequest.Delete(WebAPIController.Instance.Host + $"/api/CharacterCalendar/topic/{calId}/{type}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		request.downloadHandler = new DownloadHandlerBuffer();
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			ErrorCodePacket obj = JsonUtility.FromJson<ErrorCodePacket>(text);
			onResult(obj);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterCalendar/topic/{calId}/{type}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static IEnumerator DeleteComment(Action<ErrorCodePacket> onResult, Action<UnityWebRequest> onError, ulong topicId, ulong commentId, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = UnityWebRequest.Delete(WebAPIController.Instance.Host + $"/api/CharacterCalendar/comment/{topicId}/{commentId}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		request.downloadHandler = new DownloadHandlerBuffer();
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			ErrorCodePacket obj = JsonUtility.FromJson<ErrorCodePacket>(text);
			onResult(obj);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterCalendar/comment/{topicId}/{commentId}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static IEnumerator PutTopic(Action<ErrorCodePacket> onResult, Action<UnityWebRequest> onError, CalendarTopic value, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + "/api/CharacterCalendar/topic/";
		string json2 = string.Empty;
		json2 += JsonUtility.ToJson(value);
		byte[] bodyRaw = Encoding.UTF8.GetBytes(json2);
		request.uploadHandler = new UploadHandlerRaw(bodyRaw);
		request.downloadHandler = new DownloadHandlerBuffer();
		request.SetRequestHeader("Content-Type", "application/json");
		request.SetRequestHeader("charset", "UTF=8");
		request.method = "PUT";
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
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterCalendar/topic/");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static IEnumerator PutComment(Action<ErrorCodePacket> onResult, Action<UnityWebRequest> onError, TopicComment value, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + "/api/CharacterCalendar/comment/";
		string json2 = string.Empty;
		json2 += JsonUtility.ToJson(value);
		byte[] bodyRaw = Encoding.UTF8.GetBytes(json2);
		request.uploadHandler = new UploadHandlerRaw(bodyRaw);
		request.downloadHandler = new DownloadHandlerBuffer();
		request.SetRequestHeader("Content-Type", "application/json");
		request.SetRequestHeader("charset", "UTF=8");
		request.method = "PUT";
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
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterCalendar/comment/");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static IEnumerator GetBoardTopic(Action<CalendarTopicParam> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetBoardTopic.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/CharacterCalendar/board/");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CalendarTopicParam calendarTopicParam = JsonUtility.FromJson<CalendarTopicParam>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CalendarTopicParam> cacheValue = new CacheValue<CalendarTopicParam>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = calendarTopicParam;
				Cache_GetBoardTopic[cacheKey] = cacheValue;
			}
			onResult(calendarTopicParam);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterCalendar/board/");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetBoardTopic()
	{
		Cache_GetBoardTopic.Clear();
	}

	public static void ClearCache()
	{
		Cache_GetTopicStringInt32Int32Int32Int32Int32.Clear();
		Cache_GetSelectTopicInt32UInt64.Clear();
		Cache_GetAbstractInt32Int32.Clear();
		Cache_GetTopicUpdatedInfo.Clear();
		Cache_GetCommentUInt64UInt32.Clear();
		Cache_GetBoardTopic.Clear();
	}
}
