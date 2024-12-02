using System;
using System.Collections;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.Networking;

namespace WebRequest;

public class Friend
{
	private static Dictionary<string, CacheValue<CharacterMemberList>> Cache_GetMember = new Dictionary<string, CacheValue<CharacterMemberList>>();

	public static IEnumerator GetMember(Action<CharacterMemberList> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
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
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/friend/member");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterMemberList characterMemberList = JsonUtility.FromJson<CharacterMemberList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CharacterMemberList> cacheValue = new CacheValue<CharacterMemberList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = characterMemberList;
				Cache_GetMember[cacheKey] = cacheValue;
			}
			onResult(characterMemberList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/friend/member");
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
