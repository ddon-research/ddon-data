using System;
using System.Collections;
using System.Text;
using Packet;
using UnityEngine;
using UnityEngine.Networking;

namespace WebRequest;

public class Report
{
	public static IEnumerator PostTopic(Action<ErrorCodePacket> onResult, Action<UnityWebRequest> onError, ReportTopicInfo value, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		UnityWebRequest request = new UnityWebRequest();
		request.url = WebAPIController.Instance.Host + "/api/ReportController/topic/";
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
			WebAPIController.Instance.HandleError(request, onError, "api/ReportController/topic/");
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
