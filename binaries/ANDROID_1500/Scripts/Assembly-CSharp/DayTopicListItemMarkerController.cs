using System.Collections;
using Packet;
using UnityEngine;
using UnityEngine.UI;

public class DayTopicListItemMarkerController : MonoBehaviour
{
	private IEnumerator routine;

	private Image _MyImage;

	public Image MyImage
	{
		get
		{
			if (_MyImage == null)
			{
				_MyImage = GetComponent<Image>();
			}
			return _MyImage;
		}
		set
		{
			_MyImage = value;
		}
	}

	private void OnEnable()
	{
		if (routine != null)
		{
			StartCoroutine(routine);
		}
	}

	public void LoadImageAsync(CalendarTopic.CALENDAR_TYPE type)
	{
		MyImage.enabled = true;
		string text = "bg_day_frame_private";
		switch (type)
		{
		case CalendarTopic.CALENDAR_TYPE.PRIVATE:
			text = "bg_day_frame_private";
			break;
		case CalendarTopic.CALENDAR_TYPE.CLAN:
			text = "bg_day_frame_clan";
			break;
		case CalendarTopic.CALENDAR_TYPE.EVENT:
			text = "bg_day_frame_official";
			break;
		}
		string filePath = "Images/calendar/list/" + text;
		routine = LoadManager.LoadAsync(filePath, delegate(Sprite res)
		{
			if (MyImage != null)
			{
				MyImage.sprite = res;
			}
		});
		if (base.gameObject.activeInHierarchy)
		{
			StartCoroutine(routine);
		}
	}
}
