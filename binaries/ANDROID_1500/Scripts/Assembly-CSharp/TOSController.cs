using System;
using System.Collections;
using System.IO;
using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(Text))]
public class TOSController : MonoBehaviour
{
	private Text TosText;

	private void Start()
	{
		TosText = GetComponent<Text>();
	}

	private void OnEnable()
	{
		SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		StartCoroutine(LoadTos(ImageDownloader.CDNHost + "etc/", delegate(string text)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			TosText.text = text;
			for (int i = 0; i < 10; i++)
			{
				TosText.text += Environment.NewLine;
			}
		}, delegate(string errText)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			SingletonMonoBehaviour<ModalDialog>.Instance.Error(ModalDialog.Mode.OK, "エラー", errText);
		}));
	}

	private void OnLoadText(string text)
	{
		using StringReader stringReader = new StringReader(text);
		uint result = 0u;
		uint.TryParse(stringReader.ReadLine(), out result);
	}

	public static IEnumerator LoadTos(string url, Action<string> onLoadText, Action<string> onError, int retryNum = 2)
	{
		WWW www = new WWW(url + "tos.txt");
		yield return www;
		if (www.error == null)
		{
			string obj = www.text.Clone().ToString();
			onLoadText(obj);
		}
		else if (retryNum == 0)
		{
			onError("利用規約の取得に失敗");
		}
		else
		{
			yield return LoadTos(url, onLoadText, onError, retryNum - 1);
		}
	}
}
