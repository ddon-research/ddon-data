using System;
using System.Collections;
using UnityEngine;

public class ImageDownloader
{
	public static string CDNHost = "https://debug-companion-img.dd-on.net:1443/";

	public static IEnumerator Download(string url, Action<Texture2D> onResult)
	{
		WWW www = new WWW(url);
		yield return www;
		if (onResult != null)
		{
			if (www.error == null)
			{
				onResult(www.textureNonReadable);
				yield break;
			}
			Debug.LogError(www.error);
			onResult(null);
		}
	}
}
