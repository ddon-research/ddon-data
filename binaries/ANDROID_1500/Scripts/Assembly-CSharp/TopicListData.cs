using System;
using Packet;
using UnityEngine;
using UnityEngine.UI;

public class TopicListData : TableViewCell<CalendarTopic>
{
	private CalendarTopic _Topic;

	[SerializeField]
	private ListedLabel StartDate;

	[SerializeField]
	private ListedLabel EndDate;

	[SerializeField]
	private ListedLabel EndDateOnly;

	[SerializeField]
	private new Text Title;

	[SerializeField]
	private Text Like;

	[SerializeField]
	private GameObject LikeObject;

	[SerializeField]
	private Text LastUpdate;

	[SerializeField]
	private Text Comment;

	[SerializeField]
	private GameObject CommentObject;

	[SerializeField]
	private GameObject PeriodInfo;

	[SerializeField]
	private GameObject PrivateIcon;

	[SerializeField]
	private GameObject ClanIcon;

	[SerializeField]
	private GameObject OfficialIcon;

	[SerializeField]
	private Button Button;

	[SerializeField]
	public GameObject NewIcon;

	public CalendarTopic Topic
	{
		get
		{
			return _Topic;
		}
		private set
		{
			_Topic = value;
		}
	}

	public override void UpdateContent(CalendarTopic topic)
	{
		if (topic.TopicId == 0)
		{
			return;
		}
		Topic = topic;
		DateTime date = DateTime.Parse(topic.BeginDate);
		DateTime date2 = DateTime.Parse(topic.EndDate);
		DateTime dateTime = DateTime.Parse(topic.ModifiedAt);
		StartDate.gameObject.SetActive(value: false);
		EndDate.gameObject.SetActive(value: false);
		EndDateOnly.gameObject.SetActive(value: false);
		if (topic.BeginDate != "1900-01-01T00:00:00+09:00")
		{
			StartDate.UpdateContent(date);
			StartDate.gameObject.SetActive(value: true);
			if (topic.EndDate != "2100-01-01T00:00:00+09:00")
			{
				EndDate.UpdateContent(date2);
				EndDate.gameObject.SetActive(value: true);
			}
		}
		else if (topic.EndDate != "2100-01-01T00:00:00+09:00")
		{
			EndDateOnly.UpdateContent(date2);
			EndDateOnly.gameObject.SetActive(value: true);
		}
		Title.text = topic.Title;
		if (topic.Title.Length > 36)
		{
			string text = topic.Title.Substring(0, 35) + "...";
			Title.text = text;
		}
		Like.text = topic.LikeNum.ToString();
		LastUpdate.text = dateTime.ToString("yyyy.MM.dd HH:mm:ss");
		Comment.text = topic.CommentNum.ToString();
		if (date2.CompareTo(DateTime.Now) > 0 && PeriodInfo != null)
		{
			PeriodInfo.SetActive(value: false);
		}
		PrivateIcon.SetActive(value: false);
		OfficialIcon.SetActive(value: false);
		ClanIcon.SetActive(value: false);
		CommentObject.SetActive(value: false);
		LikeObject.SetActive(value: false);
		CheckReadIcon(topic);
		if (topic.Type == CalendarTopic.CALENDAR_TYPE.PRIVATE)
		{
			NewIcon.SetActive(value: false);
		}
		Button.onClick.RemoveAllListeners();
		switch (topic.Type)
		{
		case CalendarTopic.CALENDAR_TYPE.PRIVATE:
			PrivateIcon.SetActive(value: true);
			Button.onClick.AddListener(delegate
			{
				SingletonMonoBehaviour<CalendarManager>.Instance.PrivateTopicDetail.UpdateContent(topic);
				SingletonMonoBehaviour<NavigationViewController>.Instance.Push(SingletonMonoBehaviour<CalendarManager>.Instance.PrivateTopicDetail);
			});
			break;
		case CalendarTopic.CALENDAR_TYPE.CLAN:
			ClanIcon.SetActive(value: true);
			CommentObject.SetActive(value: true);
			LikeObject.SetActive(value: true);
			Button.onClick.AddListener(delegate
			{
				SingletonMonoBehaviour<CalendarManager>.Instance.ClanTopicDetail.UpdateContent(topic);
				SingletonMonoBehaviour<NavigationViewController>.Instance.Push(SingletonMonoBehaviour<CalendarManager>.Instance.ClanTopicDetail);
			});
			break;
		case CalendarTopic.CALENDAR_TYPE.EVENT:
			OfficialIcon.SetActive(value: true);
			LikeObject.SetActive(value: true);
			Button.onClick.AddListener(delegate
			{
				SingletonMonoBehaviour<CalendarManager>.Instance.OfficialTopicDetail.UpdateContent(topic, isTypedList: true);
				SingletonMonoBehaviour<NavigationViewController>.Instance.Push(SingletonMonoBehaviour<CalendarManager>.Instance.OfficialTopicDetail);
			});
			break;
		}
	}

	private void CheckReadIcon(CalendarTopic topic)
	{
		bool flag = SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.DidReadTopic(topic.Type, topic.TopicId);
		NewIcon.SetActive(!flag);
	}

	public void OnEnable()
	{
		if (Topic != null)
		{
			CheckReadIcon(Topic);
		}
	}
}
