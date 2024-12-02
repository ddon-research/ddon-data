using System;
using System.Collections;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.Networking;

namespace WebRequest;

public class Clan
{
	private static Dictionary<string, CacheValue<ClanMemberList>> Cache_GetMember = new Dictionary<string, CacheValue<ClanMemberList>>();

	public static IEnumerator GetMember(Action<ClanMemberList> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		if (!cacheOption.IgnoreCache && Cache_GetMember.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/clan/member");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			ClanMemberList clanMemberList = JsonUtility.FromJson<ClanMemberList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<ClanMemberList> cacheValue = new CacheValue<ClanMemberList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = clanMemberList;
				Cache_GetMember[cacheKey] = cacheValue;
			}
			onResult(clanMemberList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/clan/member");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetMember()
	{
		Cache_GetMember.Clear();
	}

	public static void ClearCache()
	{
		Cache_GetMember.Clear();
	}
}
