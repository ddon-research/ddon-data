using System;
using System.Collections;
using UnityEngine;

public class LoadManager : MonoBehaviour
{
	public static IEnumerator LoadAsync<T>(string filePath, Action<T> onComplete) where T : UnityEngine.Object
	{
		ResourceRequest resReq = Resources.LoadAsync<T>(filePath);
		while (!resReq.isDone)
		{
			yield return null;
		}
		onComplete(resReq.asset as T);
	}

	public static IEnumerator LoadAsync<T, V>(string filePath, Action<T, V> onComplete, V obj) where T : UnityEngine.Object
	{
		ResourceRequest resReq = Resources.LoadAsync<T>(filePath);
		while (!resReq.isDone)
		{
			yield return null;
		}
		onComplete(resReq.asset as T, obj);
	}
}
