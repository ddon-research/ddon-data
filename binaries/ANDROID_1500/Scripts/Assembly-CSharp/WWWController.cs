using System.Collections;
using UnityEngine;

public class WWWController : MonoBehaviour
{
	public float timeOut = 10f;

	[HideInInspector]
	public WWW result;

	[HideInInspector]
	public bool isTimeOut;

	public IEnumerator Request(string url)
	{
		Dispose();
		WWW www = new WWW(url);
		float endTime = Time.realtimeSinceStartup + timeOut;
		while (!www.isDone)
		{
			if (Time.realtimeSinceStartup > endTime)
			{
				www.Dispose();
				isTimeOut = true;
				yield break;
			}
			yield return 0;
		}
		result = www;
	}

	public void Dispose()
	{
		if (result != null)
		{
			result.Dispose();
			result = null;
		}
	}
}
