using System.Collections;
using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementTopImage : ServerUIElementBase
{
	[SerializeField]
	private RawImage BG;

	public override void SetupElement()
	{
		BG.gameObject.SetActive(value: false);
		StartCoroutine(LoadImage(DispParam.Text1));
	}

	private IEnumerator LoadImage(string url)
	{
		WWW www = new WWW(ImageDownloader.CDNHost + url);
		yield return www;
		if (www.error == null)
		{
			BG.texture = www.textureNonReadable;
			BG.gameObject.SetActive(value: true);
		}
		yield return null;
	}
}
