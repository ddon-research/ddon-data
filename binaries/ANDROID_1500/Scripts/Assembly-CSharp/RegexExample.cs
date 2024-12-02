using UnityEngine;

public class RegexExample : MonoBehaviour
{
	[SerializeField]
	private RegexHypertext _text;

	private const string RegexURL = "http(s)?://([\\w-]+\\.)+[\\w-]+(/[\\w- ./?%&=]*)?";

	private const string RegexHashtag = "[#＃][Ａ-Ｚａ-ｚA-Za-z一-鿆0-9０-９ぁ-ヶｦ-ﾟー]+";

	private void Start()
	{
		_text.SetClickableByRegex("http(s)?://([\\w-]+\\.)+[\\w-]+(/[\\w- ./?%&=]*)?", Color.cyan, delegate(string url)
		{
			Debug.Log(url);
		});
		_text.SetClickableByRegex("[#＃][Ａ-Ｚａ-ｚA-Za-z一-鿆0-9０-９ぁ-ヶｦ-ﾟー]+", Color.green, delegate(string hashtag)
		{
			Debug.Log(hashtag);
		});
	}
}
