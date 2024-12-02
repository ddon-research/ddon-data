using System;
using Packet;
using UnityEngine;
using UnityEngine.UI;

public class DayTopicListData : TableViewCell<CalendarTopic>
{
	[SerializeField]
	private Text PeriodText;

	[SerializeField]
	private Text TopicTitle;

	[SerializeField]
	private Text Like;

	[SerializeField]
	private GameObject LikeObject;

	[SerializeField]
	private Text Comment;

	[SerializeField]
	private GameObject CommentObject;

	[SerializeField]
	private Text LastUpdate;

	[SerializeField]
	private GameObject PrivateIcon;

	[SerializeField]
	private GameObject ClanIcon;

	[SerializeField]
	private GameObject OfficialIcon;

	[SerializeField]
	private Button Button;

	public CalendarTopic DataSource;

	[SerializeField]
	private DayTopicListItemMarkerController MyMarker;

	public new CalendarTopic.CALENDAR_TYPE GetType()
	{
		if (DataSource != null)
		{
			return DataSource.Type;
		}
		return CalendarTopic.CALENDAR_TYPE.NONE;
	}

	public override void UpdateContent(CalendarTopic source)
	{
		DataSource = source;
		CalendarTopic topic = source;
		if (topic.TopicId != 0)
		{
			MyMarker.LoadImageAsync(topic.Type);
			SetIcon(topic.Type);
			DateTime begin = DateTime.Parse(topic.BeginDate);
			DateTime end = DateTime.Parse(topic.EndDate);
			DateTime dateTime = DateTime.Parse(topic.ModifiedAt);
			TopicTitle.text = topic.Title;
			if (topic.Title.Length > 46)
			{
				string text = topic.Title.Substring(0, 45) + "...";
				TopicTitle.text = text;
			}
			LastUpdate.text = dateTime.ToString("yyyy.MM.dd HH:mm:ss");
			Like.text = topic.LikeNum.ToString();
			Comment.text = topic.CommentNum.ToString();
			LikeObject.SetActive(value: false);
			CommentObject.SetActive(value: false);
			switch (topic.Type)
			{
			case CalendarTopic.CALENDAR_TYPE.CLAN:
				CommentObject.SetActive(value: true);
				LikeObject.SetActive(value: true);
				break;
			case CalendarTopic.CALENDAR_TYPE.EVENT:
				LikeObject.SetActive(value: true);
				break;
			}
			DateTime selectDate = SingletonMonoBehaviour<CalendarManager>.Instance.DayListView.MyController.SelectDate;
			bool isIndefiniteBegin = "1900-01-01T00:00:00+09:00" == topic.BeginDate;
			bool isIndefiniteEnd = "2100-01-01T00:00:00+09:00" == topic.EndDate;
			PeriodText.text = CreateDateText(begin, end, selectDate, isIndefiniteBegin, isIndefiniteEnd);
			TopicDetail detail = SingletonMonoBehaviour<CalendarManager>.Instance.DayListView.MyController.GetTopicDetail(topic.Type);
			Button.onClick.RemoveAllListeners();
			Button.onClick.AddListener(delegate
			{
				detail.UpdateContent(topic);
				SingletonMonoBehaviour<NavigationViewController>.Instance.Push(detail);
			});
		}
	}

	private void SetIcon(CalendarTopic.CALENDAR_TYPE type)
	{
		PrivateIcon.SetActive(value: false);
		OfficialIcon.SetActive(value: false);
		ClanIcon.SetActive(value: false);
		switch (type)
		{
		case CalendarTopic.CALENDAR_TYPE.PRIVATE:
			PrivateIcon.SetActive(value: true);
			break;
		case CalendarTopic.CALENDAR_TYPE.CLAN:
			ClanIcon.SetActive(value: true);
			break;
		case CalendarTopic.CALENDAR_TYPE.EVENT:
			OfficialIcon.SetActive(value: true);
			break;
		}
	}

	private string CreateDateText(DateTime begin, DateTime end, DateTime select, bool IsIndefiniteBegin, bool IsIndefiniteEnd)
	{
		if (IsIndefiniteBegin && IsIndefiniteEnd)
		{
			return "期間指定なし";
		}
		if (IsIndefiniteBegin && !IsIndefiniteEnd)
		{
			return "指定なし～\n" + end.ToString("MM/dd") + "まで";
		}
		if (!IsIndefiniteBegin && IsIndefiniteEnd)
		{
			return begin.ToString("MM/dd") + "～\n指定なし";
		}
		DateTime dateTime = select.AddDays(1.0);
		if (select.CompareTo(begin) <= 0 && dateTime.CompareTo(begin) > 0)
		{
			if (select.CompareTo(end) <= 0 && dateTime.CompareTo(end) > 0)
			{
				return begin.ToString("HH:mm") + "\n～" + end.ToString("HH:mm");
			}
			uint num = 2u;
			DateTime dateTime2 = new DateTime(begin.Year, begin.Month, begin.Day).AddDays(1.0);
			DateTime dateTime3 = new DateTime(end.Year, end.Month, end.Day);
			num += (uint)(dateTime3 - dateTime2).Days;
			return begin.ToString("HH:mm") + "\n～" + num + "日間";
		}
		if (select.CompareTo(end) <= 0 && dateTime.CompareTo(end) > 0)
		{
			return "最終日\n～" + end.ToString("HH:mm");
		}
		uint num2 = 2u;
		DateTime dateTime4 = new DateTime(begin.Year, begin.Month, begin.Day).AddDays(1.0);
		DateTime dateTime5 = new DateTime(end.Year, end.Month, end.Day);
		TimeSpan timeSpan = dateTime5 - dateTime4;
		num2 += (uint)timeSpan.Days;
		DateTime value = dateTime4;
		uint num3;
		for (num3 = 1u; num3 <= timeSpan.Days; num3++)
		{
			value = value.AddDays(1.0);
			if (select.CompareTo(value) < 0)
			{
				break;
			}
		}
		num3++;
		return num3 + "/" + num2 + "日目\n終日";
	}
}
