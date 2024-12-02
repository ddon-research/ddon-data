using UnityEngine;
using UnityEngine.Analytics;
using UnityEngine.EventSystems;
using UnityEngine.UI;

[RequireComponent(typeof(RawImage))]
[RequireComponent(typeof(Button))]
internal class BannerElement : ViewController
{
	private string Href;

	public void Awake()
	{
	}

	public void UpdateContent(BannerData data)
	{
		Href = data.LinkURL;
		GetComponent<RawImage>().texture = data.Texture;
	}

	public void OnClick(BaseEventData eventData)
	{
		PointerEventData pointerEventData = (PointerEventData)eventData;
		if (pointerEventData != null)
		{
			Vector2 vector = pointerEventData.position - pointerEventData.pressPosition;
			if (!(vector.x >= 50f) && !(vector.x <= -50f))
			{
				Application.OpenURL(Href);
				Analytics.CustomEvent("ClickBanner");
			}
		}
	}
}
