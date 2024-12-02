using System;
using System.Collections;
using System.Text;
using Packet;
using UnityEngine;
using UnityEngine.Networking;

namespace WebRequest;

public class UserLogin
{
	public static IEnumerator Post(Action<LoginCharacterList> onResult, Action<UnityWebRequest> onError, string token, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + "/api/UserLogin";
		string json2 = string.Empty;
		json2 = json2 + "\"" + token + "\"";
		byte[] bodyRaw = Encoding.UTF8.GetBytes(json2);
		request.uploadHandler = new UploadHandlerRaw(bodyRaw);
		request.downloadHandler = new DownloadHandlerBuffer();
		request.SetRequestHeader("Content-Type", "application/json");
		request.SetRequestHeader("charset", "UTF=8");
		request.method = "POST";
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			LoginCharacterList obj = JsonUtility.FromJson<LoginCharacterList>(text);
			onResult(obj);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/UserLogin");
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
