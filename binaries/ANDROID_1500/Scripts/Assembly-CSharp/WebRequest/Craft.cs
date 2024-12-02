using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using Packet;
using UnityEngine;
using UnityEngine.Networking;

namespace WebRequest;

public class Craft
{
	private static Dictionary<string, CacheValue<CraftCategoryList>> Cache_GetMainCategory = new Dictionary<string, CacheValue<CraftCategoryList>>();

	private static Dictionary<string, CacheValue<CraftCategoryList>> Cache_GetSubCategoryUInt32 = new Dictionary<string, CacheValue<CraftCategoryList>>();

	private static Dictionary<string, CacheValue<CraftRecipeList>> Cache_GetRecipeListUInt32UInt32 = new Dictionary<string, CacheValue<CraftRecipeList>>();

	private static Dictionary<string, CacheValue<CraftRecipeDetail>> Cache_GetRecipeDetailUInt32 = new Dictionary<string, CacheValue<CraftRecipeDetail>>();

	private static Dictionary<string, CacheValue<CraftPawnList>> Cache_GetPawn = new Dictionary<string, CacheValue<CraftPawnList>>();

	private static Dictionary<string, CacheValue<CraftExpRate>> Cache_GetExpRate = new Dictionary<string, CacheValue<CraftExpRate>>();

	private static Dictionary<string, CacheValue<CraftPawnList>> Cache_GetSupportPawn = new Dictionary<string, CacheValue<CraftPawnList>>();

	private static Dictionary<string, CacheValue<CraftPawnStatusList>> Cache_GetPawnStatus = new Dictionary<string, CacheValue<CraftPawnStatusList>>();

	private static Dictionary<string, CacheValue<CraftAppDiscount>> Cache_GetAppDiscount = new Dictionary<string, CacheValue<CraftAppDiscount>>();

	public static IEnumerator GetMainCategory(Action<CraftCategoryList> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetMainCategory.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/craft/main_category");
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CraftCategoryList craftCategoryList = JsonUtility.FromJson<CraftCategoryList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CraftCategoryList> cacheValue = new CacheValue<CraftCategoryList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = craftCategoryList;
				Cache_GetMainCategory[cacheKey] = cacheValue;
			}
			onResult(craftCategoryList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/craft/main_category");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetMainCategory()
	{
		Cache_GetMainCategory.Clear();
	}

	public static IEnumerator GetSubCategory(Action<CraftCategoryList> onResult, Action<UnityWebRequest> onError, uint mainCategoryId, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + mainCategoryId;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetSubCategoryUInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/craft/sub_category/{mainCategoryId}");
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CraftCategoryList craftCategoryList = JsonUtility.FromJson<CraftCategoryList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CraftCategoryList> cacheValue = new CacheValue<CraftCategoryList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = craftCategoryList;
				Cache_GetSubCategoryUInt32[cacheKey] = cacheValue;
			}
			onResult(craftCategoryList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/craft/sub_category/{mainCategoryId}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetSubCategoryUInt32()
	{
		Cache_GetSubCategoryUInt32.Clear();
	}

	public static IEnumerator GetRecipeList(Action<CraftRecipeList> onResult, Action<UnityWebRequest> onError, uint mainCategoryId, uint subCategoryId, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + mainCategoryId + "/" + subCategoryId;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetRecipeListUInt32UInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/craft/recipe_list/{mainCategoryId}/{subCategoryId}");
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CraftRecipeList craftRecipeList = JsonUtility.FromJson<CraftRecipeList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CraftRecipeList> cacheValue = new CacheValue<CraftRecipeList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = craftRecipeList;
				Cache_GetRecipeListUInt32UInt32[cacheKey] = cacheValue;
			}
			onResult(craftRecipeList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/craft/recipe_list/{mainCategoryId}/{subCategoryId}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetRecipeListUInt32UInt32()
	{
		Cache_GetRecipeListUInt32UInt32.Clear();
	}

	public static IEnumerator GetRecipeDetail(Action<CraftRecipeDetail> onResult, Action<UnityWebRequest> onError, uint recipeId, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + recipeId;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetRecipeDetailUInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/craft/recipe_detail/{recipeId}");
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CraftRecipeDetail craftRecipeDetail = JsonUtility.FromJson<CraftRecipeDetail>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CraftRecipeDetail> cacheValue = new CacheValue<CraftRecipeDetail>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = craftRecipeDetail;
				Cache_GetRecipeDetailUInt32[cacheKey] = cacheValue;
			}
			onResult(craftRecipeDetail);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/craft/recipe_detail/{recipeId}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetRecipeDetailUInt32()
	{
		Cache_GetRecipeDetailUInt32.Clear();
	}

	public static IEnumerator GetPawn(Action<CraftPawnList> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetPawn.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/craft/pawn");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CraftPawnList craftPawnList = JsonUtility.FromJson<CraftPawnList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CraftPawnList> cacheValue = new CacheValue<CraftPawnList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = craftPawnList;
				Cache_GetPawn[cacheKey] = cacheValue;
			}
			onResult(craftPawnList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/craft/pawn");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetPawn()
	{
		Cache_GetPawn.Clear();
	}

	public static IEnumerator GetExpRate(Action<CraftExpRate> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetExpRate.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/craft/exprate");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CraftExpRate craftExpRate = JsonUtility.FromJson<CraftExpRate>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CraftExpRate> cacheValue = new CacheValue<CraftExpRate>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = craftExpRate;
				Cache_GetExpRate[cacheKey] = cacheValue;
			}
			onResult(craftExpRate);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/craft/exprate");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetExpRate()
	{
		Cache_GetExpRate.Clear();
	}

	public static IEnumerator GetSupportPawn(Action<CraftPawnList> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetSupportPawn.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/craft/support_pawn");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CraftPawnList craftPawnList = JsonUtility.FromJson<CraftPawnList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CraftPawnList> cacheValue = new CacheValue<CraftPawnList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = craftPawnList;
				Cache_GetSupportPawn[cacheKey] = cacheValue;
			}
			onResult(craftPawnList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/craft/support_pawn");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetSupportPawn()
	{
		Cache_GetSupportPawn.Clear();
	}

	public static IEnumerator PostDoCraft(Action<DoCraftResult> onResult, Action<UnityWebRequest> onError, CraftRequest data, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + "/api/craft/do_craft";
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
			DoCraftResult obj = JsonUtility.FromJson<DoCraftResult>(text);
			onResult(obj);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/craft/do_craft");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static IEnumerator GetPawnStatus(Action<CraftPawnStatusList> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetPawnStatus.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/craft/pawn_status");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CraftPawnStatusList craftPawnStatusList = JsonUtility.FromJson<CraftPawnStatusList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CraftPawnStatusList> cacheValue = new CacheValue<CraftPawnStatusList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = craftPawnStatusList;
				Cache_GetPawnStatus[cacheKey] = cacheValue;
			}
			onResult(craftPawnStatusList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/craft/pawn_status");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetPawnStatus()
	{
		Cache_GetPawnStatus.Clear();
	}

	public static IEnumerator PostInterrupt(Action onResult, Action<UnityWebRequest> onError, uint my_pawn_id, uint recipe_id, long finish_time, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + $"/api/craft/interrupt/{my_pawn_id}/{recipe_id}/{finish_time}";
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
			WebAPIController.Instance.HandleError(request, onError, "api/craft/interrupt/{my_pawn_id}/{recipe_id}/{finish_time}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static IEnumerator PostAnalyzeResult(Action<CraftAnalyzeResultList> onResult, Action<UnityWebRequest> onError, CraftAnalyzePacket packet, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + "/api/craft/analyze_result";
		string json2 = string.Empty;
		json2 += JsonUtility.ToJson(packet);
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
			CraftAnalyzeResultList obj = JsonUtility.FromJson<CraftAnalyzeResultList>(text);
			onResult(obj);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/craft/analyze_result");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static IEnumerator GetAppDiscount(Action<CraftAppDiscount> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetAppDiscount.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/craft/app_discount");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CraftAppDiscount craftAppDiscount = JsonUtility.FromJson<CraftAppDiscount>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CraftAppDiscount> cacheValue = new CacheValue<CraftAppDiscount>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = craftAppDiscount;
				Cache_GetAppDiscount[cacheKey] = cacheValue;
			}
			onResult(craftAppDiscount);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/craft/app_discount");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetAppDiscount()
	{
		Cache_GetAppDiscount.Clear();
	}

	public static void ClearCache()
	{
		Cache_GetMainCategory.Clear();
		Cache_GetSubCategoryUInt32.Clear();
		Cache_GetRecipeListUInt32UInt32.Clear();
		Cache_GetRecipeDetailUInt32.Clear();
		Cache_GetPawn.Clear();
		Cache_GetExpRate.Clear();
		Cache_GetSupportPawn.Clear();
		Cache_GetPawnStatus.Clear();
		Cache_GetAppDiscount.Clear();
	}
}
