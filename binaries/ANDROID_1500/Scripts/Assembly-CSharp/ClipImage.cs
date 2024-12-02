using System;
using System.Collections;
using Packet;
using UnityEngine;
using UnityEngine.UI;

public class ClipImage : MonoBehaviour
{
	[SerializeField]
	private GameObject EmptyObject;

	[SerializeField]
	private RawImage DispImage;

	[SerializeField]
	private string ImgUrl;

	[SerializeField]
	private string LinkUrl;

	private RectTransform CacheRectTransform;

	[SerializeField]
	private Action OnRebuildCallback;

	[SerializeField]
	private Image ErrorImage;

	private AutoLayoutRebuilder MyRebuilder;

	public void UpdateContent(CalendarTopic.TopicImageInfo info, Action callback)
	{
		if (CacheRectTransform == null)
		{
			CacheRectTransform = DispImage.GetComponent<RectTransform>();
		}
		if (MyRebuilder == null)
		{
			MyRebuilder = GetComponent<AutoLayoutRebuilder>();
		}
		ImgUrl = info.ImageUrl;
		LinkUrl = info.LinkUrl;
		DispImage.gameObject.SetActive(value: false);
		ErrorImage.gameObject.SetActive(value: false);
		EmptyObject.SetActive(value: true);
		OnRebuildCallback = callback;
		DestroyImg();
	}

	public void DestroyImg()
	{
		Texture texture = DispImage.texture;
		if (texture != null)
		{
			UnityEngine.Object.Destroy(texture);
		}
		texture = null;
	}

	public void Show()
	{
		EmptyObject.SetActive(value: false);
		DispImage.gameObject.SetActive(value: true);
		MyRebuilder.MarkRebuild(delegate
		{
			OnRebuildCallback();
		});
		StartCoroutine(DisplayImage(ImgUrl));
	}

	private IEnumerator DisplayImage(string imgUrl)
	{
		yield return ImageDownloader.Download(imgUrl, delegate(Texture2D texture)
		{
			if (texture == null)
			{
				ErrorImage.gameObject.SetActive(value: true);
				DispImage.gameObject.SetActive(value: false);
				MyRebuilder.MarkRebuild(delegate
				{
					OnRebuildCallback();
				});
			}
			else
			{
				SetTexture(texture);
			}
		});
	}

	private void SetTexture(Texture2D texture)
	{
		ErrorImage.gameObject.SetActive(value: false);
		DispImage.texture = texture;
		float y = CacheRectTransform.sizeDelta.x * (float)texture.height / (float)texture.width;
		CacheRectTransform.sizeDelta = new Vector2(CacheRectTransform.sizeDelta.x, y);
		MyRebuilder.MarkRebuild(delegate
		{
			OnRebuildCallback();
		});
	}

	public void OnClick()
	{
		if (LinkUrl.Length > 0)
		{
			Application.OpenURL(LinkUrl);
		}
	}

	public void MarkRebuild()
	{
		MyRebuilder.MarkRebuild(delegate
		{
			OnRebuildCallback();
		});
	}
}
