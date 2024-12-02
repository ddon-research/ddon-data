using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using Packet;
using UnityEngine;
using UnityEngine.Networking;

namespace WebRequest;

public class CharacterData
{
	private static Dictionary<string, CacheValue<CharacterDataBase>> Cache_GetBase = new Dictionary<string, CacheValue<CharacterDataBase>>();

	private static Dictionary<string, CacheValue<CharacterDataDetail>> Cache_GetDetail = new Dictionary<string, CacheValue<CharacterDataDetail>>();

	private static Dictionary<string, CacheValue<CharacterAnnounce>> Cache_GetAnnounce = new Dictionary<string, CacheValue<CharacterAnnounce>>();

	private static Dictionary<string, CacheValue<CharacterPawnList>> Cache_GetPawnList = new Dictionary<string, CacheValue<CharacterPawnList>>();

	private static Dictionary<string, CacheValue<PlayerProfile>> Cache_GetCharacterProfileUInt32 = new Dictionary<string, CacheValue<PlayerProfile>>();

	private static Dictionary<string, CacheValue<MainPawnProfile>> Cache_GetCharacterMainPawnProfileUInt32 = new Dictionary<string, CacheValue<MainPawnProfile>>();

	private static Dictionary<string, CacheValue<SupportPawnProfile>> Cache_GetCharacterSupportPawnProfileUInt32UInt32 = new Dictionary<string, CacheValue<SupportPawnProfile>>();

	public static IEnumerator GetBase(Action<CharacterDataBase> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetBase.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/CharacterData/base");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterDataBase characterDataBase = JsonUtility.FromJson<CharacterDataBase>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CharacterDataBase> cacheValue = new CacheValue<CharacterDataBase>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = characterDataBase;
				Cache_GetBase[cacheKey] = cacheValue;
			}
			onResult(characterDataBase);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterData/base");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetBase()
	{
		Cache_GetBase.Clear();
	}

	public static IEnumerator GetDetail(Action<CharacterDataDetail> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetDetail.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/CharacterData/detail");
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterDataDetail characterDataDetail = JsonUtility.FromJson<CharacterDataDetail>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CharacterDataDetail> cacheValue = new CacheValue<CharacterDataDetail>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = characterDataDetail;
				Cache_GetDetail[cacheKey] = cacheValue;
			}
			onResult(characterDataDetail);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterData/detail");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetDetail()
	{
		Cache_GetDetail.Clear();
	}

	public static IEnumerator PutIcon(Action onResult, Action<UnityWebRequest> onError, uint id, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + "/api/CharacterData/icon";
		string json2 = string.Empty;
		json2 += id;
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
			_ = request.downloadHandler.text;
			onResult();
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterData/icon");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static IEnumerator GetAnnounce(Action<CharacterAnnounce> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetAnnounce.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/CharacterData/announce");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterAnnounce characterAnnounce = JsonUtility.FromJson<CharacterAnnounce>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CharacterAnnounce> cacheValue = new CacheValue<CharacterAnnounce>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = characterAnnounce;
				Cache_GetAnnounce[cacheKey] = cacheValue;
			}
			onResult(characterAnnounce);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterData/announce");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetAnnounce()
	{
		Cache_GetAnnounce.Clear();
	}

	public static IEnumerator GetPawnList(Action<CharacterPawnList> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetPawnList.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/CharacterData/pawnlist");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterPawnList characterPawnList = JsonUtility.FromJson<CharacterPawnList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CharacterPawnList> cacheValue = new CacheValue<CharacterPawnList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = characterPawnList;
				Cache_GetPawnList[cacheKey] = cacheValue;
			}
			onResult(characterPawnList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterData/pawnlist");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetPawnList()
	{
		Cache_GetPawnList.Clear();
	}

	public static IEnumerator GetCharacterProfile(Action<PlayerProfile> onResult, Action<UnityWebRequest> onError, uint characterId, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + characterId;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetCharacterProfileUInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/CharacterData/characterprofile" + "?characterId=" + characterId);
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			PlayerProfile playerProfile = JsonUtility.FromJson<PlayerProfile>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<PlayerProfile> cacheValue = new CacheValue<PlayerProfile>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = playerProfile;
				Cache_GetCharacterProfileUInt32[cacheKey] = cacheValue;
			}
			onResult(playerProfile);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterData/characterprofile");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetCharacterProfileUInt32()
	{
		Cache_GetCharacterProfileUInt32.Clear();
	}

	public static IEnumerator GetCharacterMainPawnProfile(Action<MainPawnProfile> onResult, Action<UnityWebRequest> onError, uint pawnId, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + pawnId;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetCharacterMainPawnProfileUInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/CharacterData/charactermainpawnprofile" + "?pawnId=" + pawnId);
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			MainPawnProfile mainPawnProfile = JsonUtility.FromJson<MainPawnProfile>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<MainPawnProfile> cacheValue = new CacheValue<MainPawnProfile>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = mainPawnProfile;
				Cache_GetCharacterMainPawnProfileUInt32[cacheKey] = cacheValue;
			}
			onResult(mainPawnProfile);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterData/charactermainpawnprofile");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetCharacterMainPawnProfileUInt32()
	{
		Cache_GetCharacterMainPawnProfileUInt32.Clear();
	}

	public static IEnumerator GetCharacterSupportPawnProfile(Action<SupportPawnProfile> onResult, Action<UnityWebRequest> onError, uint characterId, uint pawnId, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + characterId + "/" + pawnId;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetCharacterSupportPawnProfileUInt32UInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/CharacterData/charactersupportpawnprofile" + "?characterId=" + characterId + "&pawnId=" + pawnId);
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			SupportPawnProfile supportPawnProfile = JsonUtility.FromJson<SupportPawnProfile>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<SupportPawnProfile> cacheValue = new CacheValue<SupportPawnProfile>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = supportPawnProfile;
				Cache_GetCharacterSupportPawnProfileUInt32UInt32[cacheKey] = cacheValue;
			}
			onResult(supportPawnProfile);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/CharacterData/charactersupportpawnprofile");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetCharacterSupportPawnProfileUInt32UInt32()
	{
		Cache_GetCharacterSupportPawnProfileUInt32UInt32.Clear();
	}

	public static void ClearCache()
	{
		Cache_GetBase.Clear();
		Cache_GetDetail.Clear();
		Cache_GetAnnounce.Clear();
		Cache_GetPawnList.Clear();
		Cache_GetCharacterProfileUInt32.Clear();
		Cache_GetCharacterMainPawnProfileUInt32.Clear();
		Cache_GetCharacterSupportPawnProfileUInt32UInt32.Clear();
	}
}
