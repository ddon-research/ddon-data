using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using Packet;
using UnityEngine;
using UnityEngine.Networking;

namespace WebRequest;

public class Bazaar
{
	private static Dictionary<string, CacheValue<BazaarCategoryList>> Cache_GetMainCategoryList = new Dictionary<string, CacheValue<BazaarCategoryList>>();

	private static Dictionary<string, CacheValue<BazaarCategoryList>> Cache_GetSubCategoryListUInt32 = new Dictionary<string, CacheValue<BazaarCategoryList>>();

	private static Dictionary<string, CacheValue<BazaarItemList>> Cache_GetItemListUInt32UInt32UInt32 = new Dictionary<string, CacheValue<BazaarItemList>>();

	private static Dictionary<string, CacheValue<BazaarExhibitElementList>> Cache_GetExhibitListUInt32 = new Dictionary<string, CacheValue<BazaarExhibitElementList>>();

	private static Dictionary<string, CacheValue<BazaarExhibitLimit>> Cache_GetExhibitLimitUInt32 = new Dictionary<string, CacheValue<BazaarExhibitLimit>>();

	private static Dictionary<string, CacheValue<BazaarExhibitingStatus>> Cache_GetCharacterBazaarList = new Dictionary<string, CacheValue<BazaarExhibitingStatus>>();

	private static Dictionary<string, CacheValue<BazaarPriceHistoryList>> Cache_GetPriceHistoryUInt32 = new Dictionary<string, CacheValue<BazaarPriceHistoryList>>();

	public static IEnumerator GetMainCategoryList(Action<BazaarCategoryList> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetMainCategoryList.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/bazaar/main_category_list");
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			BazaarCategoryList bazaarCategoryList = JsonUtility.FromJson<BazaarCategoryList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<BazaarCategoryList> cacheValue = new CacheValue<BazaarCategoryList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = bazaarCategoryList;
				Cache_GetMainCategoryList[cacheKey] = cacheValue;
			}
			onResult(bazaarCategoryList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/bazaar/main_category_list");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetMainCategoryList()
	{
		Cache_GetMainCategoryList.Clear();
	}

	public static IEnumerator GetSubCategoryList(Action<BazaarCategoryList> onResult, Action<UnityWebRequest> onError, uint id, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetSubCategoryListUInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/bazaar/sub_category_list/{id}");
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			BazaarCategoryList bazaarCategoryList = JsonUtility.FromJson<BazaarCategoryList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<BazaarCategoryList> cacheValue = new CacheValue<BazaarCategoryList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = bazaarCategoryList;
				Cache_GetSubCategoryListUInt32[cacheKey] = cacheValue;
			}
			onResult(bazaarCategoryList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/bazaar/sub_category_list/{id}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetSubCategoryListUInt32()
	{
		Cache_GetSubCategoryListUInt32.Clear();
	}

	public static IEnumerator GetItemList(Action<BazaarItemList> onResult, Action<UnityWebRequest> onError, uint main_category, uint sub_category, uint rank, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + main_category + "/" + sub_category + "/" + rank;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetItemListUInt32UInt32UInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/bazaar/item_list/{main_category}/{sub_category}/{rank}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			BazaarItemList bazaarItemList = JsonUtility.FromJson<BazaarItemList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<BazaarItemList> cacheValue = new CacheValue<BazaarItemList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = bazaarItemList;
				Cache_GetItemListUInt32UInt32UInt32[cacheKey] = cacheValue;
			}
			onResult(bazaarItemList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/bazaar/item_list/{main_category}/{sub_category}/{rank}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetItemListUInt32UInt32UInt32()
	{
		Cache_GetItemListUInt32UInt32UInt32.Clear();
	}

	public static IEnumerator GetExhibitList(Action<BazaarExhibitElementList> onResult, Action<UnityWebRequest> onError, uint item_id, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + item_id;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetExhibitListUInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/bazaar/exhibit_list/{item_id}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			BazaarExhibitElementList bazaarExhibitElementList = JsonUtility.FromJson<BazaarExhibitElementList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<BazaarExhibitElementList> cacheValue = new CacheValue<BazaarExhibitElementList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = bazaarExhibitElementList;
				Cache_GetExhibitListUInt32[cacheKey] = cacheValue;
			}
			onResult(bazaarExhibitElementList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/bazaar/exhibit_list/{item_id}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetExhibitListUInt32()
	{
		Cache_GetExhibitListUInt32.Clear();
	}

	public static IEnumerator PostBuyItem(Action<BazaarBuyResult> onResult, Action<UnityWebRequest> onError, BazaarExhibitElement elemennt, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + "/api/bazaar/buy_item";
		string json2 = string.Empty;
		json2 += JsonUtility.ToJson(elemennt);
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
			BazaarBuyResult obj = JsonUtility.FromJson<BazaarBuyResult>(text);
			onResult(obj);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/bazaar/buy_item");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static IEnumerator GetExhibitLimit(Action<BazaarExhibitLimit> onResult, Action<UnityWebRequest> onError, uint item_id, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + item_id;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetExhibitLimitUInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/bazaar/exhibit_limit/{item_id}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			BazaarExhibitLimit bazaarExhibitLimit = JsonUtility.FromJson<BazaarExhibitLimit>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<BazaarExhibitLimit> cacheValue = new CacheValue<BazaarExhibitLimit>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = bazaarExhibitLimit;
				Cache_GetExhibitLimitUInt32[cacheKey] = cacheValue;
			}
			onResult(bazaarExhibitLimit);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/bazaar/exhibit_limit/{item_id}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetExhibitLimitUInt32()
	{
		Cache_GetExhibitLimitUInt32.Clear();
	}

	public static IEnumerator GetCharacterBazaarList(Action<BazaarExhibitingStatus> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetCharacterBazaarList.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/bazaar/character_bazaar_list");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			BazaarExhibitingStatus bazaarExhibitingStatus = JsonUtility.FromJson<BazaarExhibitingStatus>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<BazaarExhibitingStatus> cacheValue = new CacheValue<BazaarExhibitingStatus>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = bazaarExhibitingStatus;
				Cache_GetCharacterBazaarList[cacheKey] = cacheValue;
			}
			onResult(bazaarExhibitingStatus);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/bazaar/character_bazaar_list");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetCharacterBazaarList()
	{
		Cache_GetCharacterBazaarList.Clear();
	}

	public static IEnumerator PostExhibitItem(Action<JemResult> onResult, Action<UnityWebRequest> onError, BazaarExhibitRequest exhibitReq, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + "/api/bazaar/exhibit_item";
		string json2 = string.Empty;
		json2 += JsonUtility.ToJson(exhibitReq);
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
			WebAPIController.Instance.HandleError(request, onError, "api/bazaar/exhibit_item");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static IEnumerator PostReceiveProceeds(Action<BazaarReceiveProceedsResult> onResult, Action<UnityWebRequest> onError, BazaarRceivePrceedsRequest receiveReq, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + "/api/bazaar/receive_proceeds";
		string json2 = string.Empty;
		json2 += JsonUtility.ToJson(receiveReq);
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
			BazaarReceiveProceedsResult obj = JsonUtility.FromJson<BazaarReceiveProceedsResult>(text);
			onResult(obj);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/bazaar/receive_proceeds");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static IEnumerator PostInterrupt(Action onResult, Action<UnityWebRequest> onError, ulong id, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + $"/api/bazaar/interrupt/{id}";
		request.downloadHandler = new DownloadHandlerBuffer();
		request.SetRequestHeader("Content-Type", "application/json");
		request.SetRequestHeader("charset", "UTF=8");
		request.method = "POST";
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			_ = request.downloadHandler.text;
			onResult();
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/bazaar/interrupt/{id}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static IEnumerator GetPriceHistory(Action<BazaarPriceHistoryList> onResult, Action<UnityWebRequest> onError, uint item_id, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + item_id;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetPriceHistoryUInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/bazaar/price_history/{item_id}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			BazaarPriceHistoryList bazaarPriceHistoryList = JsonUtility.FromJson<BazaarPriceHistoryList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<BazaarPriceHistoryList> cacheValue = new CacheValue<BazaarPriceHistoryList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = bazaarPriceHistoryList;
				Cache_GetPriceHistoryUInt32[cacheKey] = cacheValue;
			}
			onResult(bazaarPriceHistoryList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/bazaar/price_history/{item_id}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetPriceHistoryUInt32()
	{
		Cache_GetPriceHistoryUInt32.Clear();
	}

	public static void ClearCache()
	{
		Cache_GetMainCategoryList.Clear();
		Cache_GetSubCategoryListUInt32.Clear();
		Cache_GetItemListUInt32UInt32UInt32.Clear();
		Cache_GetExhibitListUInt32.Clear();
		Cache_GetExhibitLimitUInt32.Clear();
		Cache_GetCharacterBazaarList.Clear();
		Cache_GetPriceHistoryUInt32.Clear();
	}
}
