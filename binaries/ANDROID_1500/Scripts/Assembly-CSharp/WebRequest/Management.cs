using System;
using System.Collections;
using UnityEngine.Networking;

namespace WebRequest;

public class Management
{
	public static IEnumerator GetPing(Action onResult, Action<UnityWebRequest> onError, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/management/ping");
		yield return request.Send();
		if (request.responseCode == 200)
		{
			_ = request.downloadHandler.text;
			onResult();
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "management/ping");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache()
	{
	}
}
