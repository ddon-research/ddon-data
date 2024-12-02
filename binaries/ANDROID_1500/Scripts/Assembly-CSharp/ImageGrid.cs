using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.Events;

public class ImageGrid : MonoBehaviour
{
	[SerializeField]
	protected ClipImage ClipImagePrefab;

	private List<ClipImage> ImageList = new List<ClipImage>();

	[SerializeField]
	private UnityEvent OnRebuildCallback;

	[SerializeField]
	private AutoLayoutRebuilder MyRebuilder;

	public void UpdateContent(List<CalendarTopic.TopicImageInfo> list)
	{
		if (MyRebuilder == null)
		{
			MyRebuilder = GetComponent<AutoLayoutRebuilder>();
		}
		InitPhoto(list);
		MyRebuilder.MarkRebuild(delegate
		{
			OnRebuildCallback.Invoke();
		});
	}

	public void InitPhoto(List<CalendarTopic.TopicImageInfo> imgInfoList)
	{
		int num = 0;
		for (num = 0; num < ImageList.Count; num++)
		{
			if (num < imgInfoList.Count)
			{
				CalendarTopic.TopicImageInfo topicImageInfo = imgInfoList[num];
				ImageList[num].UpdateContent(topicImageInfo, delegate
				{
					MyRebuilder.MarkRebuild(delegate
					{
						OnRebuildCallback.Invoke();
					});
				});
				ImageList[num].gameObject.SetActive(value: true);
				if (topicImageInfo.IsOpen)
				{
					ImageList[num].Show();
				}
			}
			else
			{
				ImageList[num].gameObject.SetActive(value: false);
			}
		}
		int num2 = imgInfoList.Count - num;
		for (int i = 0; i < num2; i++)
		{
			ClipImage clipImage = Object.Instantiate(ClipImagePrefab);
			clipImage.transform.parent = base.transform;
			clipImage.transform.localScale = new Vector3(1f, 1f, 1f);
			clipImage.gameObject.SetActive(value: true);
			CalendarTopic.TopicImageInfo topicImageInfo2 = imgInfoList[num + i];
			clipImage.UpdateContent(topicImageInfo2, delegate
			{
				MyRebuilder.MarkRebuild(delegate
				{
					OnRebuildCallback.Invoke();
				});
			});
			ImageList.Add(clipImage);
			if (topicImageInfo2.IsOpen)
			{
				clipImage.Show();
			}
		}
	}

	public void MarkRebuild()
	{
		foreach (ClipImage image in ImageList)
		{
			image.MarkRebuild();
		}
	}

	public bool IsPhoto(CalendarTopic.TopicImageInfo info)
	{
		if (info.ImageUrl.Length > 0 && info.LinkUrl.Length == 0)
		{
			return true;
		}
		return false;
	}

	public void DestroyImages()
	{
		foreach (ClipImage image in ImageList)
		{
			image.DestroyImg();
		}
	}
}
