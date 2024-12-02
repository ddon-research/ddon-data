using System;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.UI;

public class DayButton : MonoBehaviour
{
	[SerializeField]
	private Text DayNum;

	[SerializeField]
	private GameObject MarkersPrefab;

	[SerializeField]
	private GameObject MarkerPrefab;

	[SerializeField]
	private GameObject MyMarkers;

	[SerializeField]
	private GameObject DayHighlightPrefab;

	public void CheckAbstract(DateTime date, List<CalendarAbstract> abstList, Dictionary<CalendarTopic.CALENDAR_TYPE, CalendarMarkerFilterData> filterDic)
	{
		if (DayNum.text == string.Empty)
		{
			return;
		}
		int day = int.Parse(DayNum.text);
		DateTime value = new DateTime(date.Year, date.Month, day);
		DateTime value2 = value.AddDays(1.0);
		HashSet<CalendarTopic.CALENDAR_TYPE> hashSet = new HashSet<CalendarTopic.CALENDAR_TYPE>();
		foreach (CalendarAbstract abst in abstList)
		{
			DateTime dateTime = DateTime.Parse(abst.BeginDate);
			DateTime dateTime2 = DateTime.Parse(abst.EndDate);
			if (filterDic == null || !filterDic.ContainsKey(abst.Type))
			{
				continue;
			}
			CalendarMarkerFilterData calendarMarkerFilterData = filterDic[abst.Type];
			if (!calendarMarkerFilterData.IsEnable)
			{
				continue;
			}
			switch (calendarMarkerFilterData.FilterType)
			{
			case CalendarController.MARKER_FILTER_TYPE.BEGIN_ONLY:
				if (dateTime.CompareTo(value) >= 0 && dateTime.CompareTo(value2) < 0)
				{
					hashSet.Add(abst.Type);
				}
				break;
			case CalendarController.MARKER_FILTER_TYPE.ALL:
				if (dateTime.CompareTo(value2) < 0 && dateTime2.CompareTo(value) >= 0)
				{
					hashSet.Add(abst.Type);
				}
				break;
			case CalendarController.MARKER_FILTER_TYPE.BEGIN_AND_END:
				if (dateTime.CompareTo(value) >= 0 && dateTime.CompareTo(value2) < 0)
				{
					hashSet.Add(abst.Type);
				}
				else if (dateTime2.CompareTo(value2) < 0 && dateTime2.CompareTo(value) >= 0)
				{
					hashSet.Add(abst.Type);
				}
				break;
			}
		}
		AddMarker(hashSet);
	}

	private void AddMarker(HashSet<CalendarTopic.CALENDAR_TYPE> markers)
	{
		if (markers.Count == 0)
		{
			return;
		}
		GameObject gameObject = UnityEngine.Object.Instantiate(MarkersPrefab);
		gameObject.transform.SetParent(base.transform);
		gameObject.transform.localScale = new Vector3(1f, 1f, 1f);
		RectTransform component = gameObject.GetComponent<RectTransform>();
		RectTransform component2 = MarkersPrefab.GetComponent<RectTransform>();
		Vector2 anchoredPosition = component2.anchoredPosition;
		Vector2 sizeDelta = component2.sizeDelta;
		Vector3 localPosition = component2.localPosition;
		component.anchoredPosition = anchoredPosition;
		component.sizeDelta = sizeDelta;
		component.localPosition = localPosition;
		foreach (CalendarTopic.CALENDAR_TYPE marker in markers)
		{
			GameObject mark = UnityEngine.Object.Instantiate(MarkerPrefab);
			mark.transform.SetParent(gameObject.transform);
			mark.transform.localScale = new Vector3(1f, 1f, 1f);
			mark.transform.SetSiblingIndex(1);
			Image markImage = mark.GetComponent<Image>();
			string text = string.Empty;
			string htmlString = "#000000FF";
			switch (marker)
			{
			case CalendarTopic.CALENDAR_TYPE.PRIVATE:
				text = "ico_marker_private";
				htmlString = "#093B56FF";
				break;
			case CalendarTopic.CALENDAR_TYPE.CLAN:
				text = "ico_marker_clan";
				htmlString = "#5A0814FF";
				break;
			case CalendarTopic.CALENDAR_TYPE.EVENT:
				text = "ico_marker_official";
				htmlString = "#474407FF";
				break;
			}
			string filePath = "Images/marker/" + text;
			Color color = default(Color);
			if (!ColorUtility.TryParseHtmlString(htmlString, out color))
			{
				color = Color.white;
			}
			StartCoroutine(LoadManager.LoadAsync(filePath, delegate(Sprite res)
			{
				if (markImage != null)
				{
					markImage.sprite = res;
					Outline component3 = mark.GetComponent<Outline>();
					component3.effectColor = color;
				}
			}));
		}
	}

	public void UpdateContent(DateTime date, DayListViewController dayListView, bool IsToday = false)
	{
		DayNum.text = date.Day.ToString();
		Button button = base.gameObject.AddComponent<Button>();
		button.onClick.AddListener(delegate
		{
			Debug.Log("DayButton:" + date.Day + "が押されました。");
			dayListView.MyController.UpdateContent(date);
			SingletonMonoBehaviour<NavigationViewController>.Instance.Push(dayListView);
		});
		if (IsToday)
		{
			GameObject gameObject = UnityEngine.Object.Instantiate(DayHighlightPrefab);
			gameObject.transform.SetParent(base.transform);
			gameObject.transform.localScale = new Vector3(1f, 1f, 1f);
			gameObject.transform.SetSiblingIndex(0);
		}
	}
}
