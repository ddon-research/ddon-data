using System.Collections;
using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementServerImage : ServerUIElementBase
{
	[SerializeField]
	private RawImage Image;

	public override void SetupElement()
	{
		if (DispParam.Param1 != 0)
		{
			Image.rectTransform.sizeDelta = new Vector2(Image.rectTransform.sizeDelta.x, DispParam.Param1);
		}
		Image.gameObject.SetActive(value: false);
		StartCoroutine(LoadImage(DispParam.Text1));
	}

	private IEnumerator LoadImage(string url)
	{
		WWW www = new WWW(ImageDownloader.CDNHost + url);
		yield return www;
		if (www.error == null)
		{
			Image.texture = www.textureNonReadable;
			if (DispParam.Param1 == 0)
			{
				Image.SetNativeSize();
			}
			Image.gameObject.SetActive(value: true);
		}
		yield return null;
	}
}
