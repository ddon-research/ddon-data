using System.Collections;
using System.Collections.Generic;
using System.Linq;
using HtmlAgilityPack;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.Networking;
using UnityEngine.UI;
using WebRequest;

public class BannerController : MonoBehaviour
{
	private static readonly string RootURL = "https://members.dd-on.jp/";

	private List<BannerData> BannerDatas;

	[SerializeField]
	private BannerElement Element;

	[SerializeField]
	private RawImage AnimationImage;

	[SerializeField]
	private BannerNaviIconController NaviIconBase;

	private List<BannerNaviIconController> NaviIcons;

	private int CurrentPageIndex;

	private void Awake()
	{
		Element.gameObject.SetActive(value: false);
		AnimationImage.gameObject.SetActive(value: false);
		NaviIconBase.gameObject.SetActive(value: false);
	}

	private void Start()
	{
		StartCoroutine(InGameURL.GetBanner(delegate(string url)
		{
			StartCoroutine(GetHtml(url));
		}, null));
	}

	private IEnumerator GetHtml(string url)
	{
		UnityWebRequest request = UnityWebRequest.Get(url);
		yield return request.Send();
		if (!string.IsNullOrEmpty(request.error))
		{
			Debug.Log(request.error);
		}
		else if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			yield return AnalyzeHTML(text);
		}
		else
		{
			Debug.Log(request.responseCode);
		}
	}

	private IEnumerator AnalyzeHTML(string html)
	{
		HtmlDocument doc = new HtmlDocument();
		doc.LoadHtml(html);
		HtmlNodeCollection nodes = doc.DocumentNode.SelectNodes("/html[1]/body[1]/div[1]/div[1]/div[1]/ul[1]/li/a");
		BannerDatas = new List<BannerData>();
		foreach (HtmlNode node in (IEnumerable<HtmlNode>)nodes)
		{
			string href = RootURL + node.Attributes.Where((HtmlAttribute a) => a.Name == "href").First().Value;
			string imgUrl = RootURL + node.FirstChild.Attributes.Where((HtmlAttribute a) => a.Name == "src").First().Value;
			yield return ImageDownloader.Download(imgUrl, delegate(Texture2D texture)
			{
				BannerDatas.Add(new BannerData
				{
					LinkURL = href,
					Texture = texture
				});
			});
		}
		NaviIcons = new List<BannerNaviIconController>();
		foreach (BannerData bannerData in BannerDatas)
		{
			_ = bannerData;
			GameObject gameObject = Object.Instantiate(NaviIconBase.gameObject);
			gameObject.SetActive(value: true);
			RectTransform component = gameObject.GetComponent<RectTransform>();
			Vector3 localScale = component.transform.localScale;
			Vector2 sizeDelta = component.sizeDelta;
			Vector2 offsetMin = component.offsetMin;
			Vector2 offsetMax = component.offsetMax;
			component.transform.SetParent(NaviIconBase.transform.parent);
			component.transform.localScale = localScale;
			component.sizeDelta = sizeDelta;
			component.offsetMin = offsetMin;
			component.offsetMax = offsetMax;
			NaviIcons.Add(gameObject.GetComponent<BannerNaviIconController>());
		}
		Element.gameObject.SetActive(value: true);
		SelectPage(0);
		NaviIcons[0].SetEnable(b: true);
	}

	private void SelectPage(int index)
	{
		Element.UpdateContent(BannerDatas[index]);
		CurrentPageIndex = index;
	}

	public void NextPage()
	{
		if (!AnimationImage.gameObject.activeSelf)
		{
			int index = CurrentPageIndex + 1;
			if (index >= BannerDatas.Count)
			{
				index = 0;
			}
			NaviIcons[CurrentPageIndex].SetEnable(b: false);
			NaviIcons[index].SetEnable(b: true);
			AnimationImage.gameObject.SetActive(value: true);
			AnimationImage.texture = BannerDatas[index].Texture;
			RectTransform component = AnimationImage.gameObject.GetComponent<RectTransform>();
			Vector2 anchoredPosition = component.anchoredPosition;
			component.anchoredPosition = new Vector2(component.rect.width, 0f);
			component.MoveTo(anchoredPosition, 0.2f, 0f, iTween.EaseType.easeOutSine, delegate
			{
				AnimationImage.gameObject.SetActive(value: false);
			});
			Vector2 anchoredPosition2 = Element.CachedRectTransform.anchoredPosition;
			anchoredPosition2.x = 0f - Element.CachedRectTransform.rect.width;
			Element.CachedRectTransform.MoveTo(anchoredPosition2, 0.2f, 0f, iTween.EaseType.easeOutSine, delegate
			{
				Element.CachedRectTransform.anchoredPosition = new Vector2(0f, 0f);
				SelectPage(index);
			});
		}
	}

	public void PrevPage()
	{
		if (!AnimationImage.gameObject.activeSelf)
		{
			int index = CurrentPageIndex - 1;
			if (index < 0)
			{
				index = BannerDatas.Count - 1;
			}
			NaviIcons[CurrentPageIndex].SetEnable(b: false);
			NaviIcons[index].SetEnable(b: true);
			AnimationImage.gameObject.SetActive(value: true);
			AnimationImage.texture = BannerDatas[index].Texture;
			RectTransform component = AnimationImage.gameObject.GetComponent<RectTransform>();
			Vector2 anchoredPosition = component.anchoredPosition;
			component.anchoredPosition = new Vector2(0f - component.rect.width, 0f);
			component.MoveTo(anchoredPosition, 0.2f, 0f, iTween.EaseType.easeOutSine, delegate
			{
				AnimationImage.gameObject.SetActive(value: false);
			});
			Vector2 anchoredPosition2 = Element.CachedRectTransform.anchoredPosition;
			anchoredPosition2.x = Element.CachedRectTransform.rect.width;
			Element.CachedRectTransform.MoveTo(anchoredPosition2, 0.2f, 0f, iTween.EaseType.easeOutSine, delegate
			{
				Element.CachedRectTransform.anchoredPosition = new Vector2(0f, 0f);
				SelectPage(index);
			});
		}
	}

	public void OnEndDrag(BaseEventData eventData)
	{
		PointerEventData pointerEventData = (PointerEventData)eventData;
		if (pointerEventData != null)
		{
			Vector2 vector = pointerEventData.position - pointerEventData.pressPosition;
			if (vector.x > 50f)
			{
				PrevPage();
			}
			else if (vector.x < -50f)
			{
				NextPage();
			}
		}
	}
}
