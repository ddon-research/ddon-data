using System;
using Packet;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.Networking;
using WebRequest;

public class EditTopic : CreateTopic
{
	[SerializeField]
	public CalendarTopic TopicData;

	[SerializeField]
	protected TopicDetail MyTopicDetail;

	[SerializeField]
	private GameObject TitleHeaderObj;

	[SerializeField]
	private GameObject TitleObj;

	[SerializeField]
	private GameObject DateHeaderObj;

	[SerializeField]
	private GameObject BeginObj;

	[SerializeField]
	private GameObject EndObj;

	[SerializeField]
	private AutoLayoutRebuilder MyRebuilder;

	[SerializeField]
	private float BoardEditHeight = 510f;

	[SerializeField]
	private RectTransform BodyScrollObject;

	private Vector2 BodyScrollObjectSize = Vector2.zero;

	public override void OnNavigationPopBegin()
	{
		TopicData = null;
		base.OnNavigationPopBegin();
	}

	public void UpdateContent(CalendarTopic topic, TopicDetail myDetail)
	{
		if (BodyScrollObjectSize == Vector2.zero)
		{
			BodyScrollObjectSize = BodyScrollObject.sizeDelta;
		}
		BodyScrollObject.sizeDelta = BodyScrollObjectSize;
		TitleHeaderObj.SetActive(value: true);
		TitleObj.SetActive(value: true);
		DateHeaderObj.SetActive(value: true);
		BeginObj.SetActive(value: true);
		EndObj.SetActive(value: true);
		ResetFields(topic.Type, BoardEditHeight);
		MyTopicDetail = myDetail;
		CalendarType = topic.Type;
		TopicData = topic;
		TopicTitle.text = topic.Title;
		Content.text = topic.Content;
		MyText.text = topic.Content;
		MyChildTextFitter.Fitting();
		if (topic.Type == CalendarTopic.CALENDAR_TYPE.CLAN_MESSAGE_BOARD)
		{
			BodyScrollObject.sizeDelta = new Vector2(BodyScrollObjectSize.x, BoardEditHeight);
			RectTransform component = InputHolder.gameObject.GetComponent<RectTransform>();
			MaskObject.sizeDelta = new Vector2(BodyOriginSize.x, BoardEditHeight);
			if (component.sizeDelta.y < MaskObject.sizeDelta.y)
			{
				component.sizeDelta = MaskObject.sizeDelta;
			}
			ContentTrans.anchoredPosition = new Vector2(BodyOriginPos.x, 0f);
			component.anchoredPosition = new Vector2(BodyOriginPos.x, 0f);
		}
		MyRebuilder.MarkRebuild();
		DateTime startDateTime = DateTime.Parse(topic.BeginDate);
		DateTime endDateTime = DateTime.Parse(topic.EndDate);
		base.StartDateTime = startDateTime;
		base.EndDateTime = endDateTime;
		SetCalendarTypeIcon();
		if (topic.Type == CalendarTopic.CALENDAR_TYPE.CLAN_MESSAGE_BOARD)
		{
			TitleHeaderObj.SetActive(value: false);
			TitleObj.SetActive(value: false);
			DateHeaderObj.SetActive(value: false);
			BeginObj.SetActive(value: false);
			EndObj.SetActive(value: false);
		}
	}

	public override void PostData()
	{
		if (!CheckData() || TopicData == null)
		{
			Debug.Log("投稿時チェックに失敗");
			return;
		}
		lock (thisLock)
		{
			if (IsPosting)
			{
				return;
			}
			IsPosting = true;
		}
		DateTime startDateTime = GetStartDateTime();
		DateTime endDateTime = GetEndDateTime();
		CalendarTopic topicData = TopicData;
		topicData.BeginDate = CalendarTopic.DateTimeToString(startDateTime);
		topicData.EndDate = CalendarTopic.DateTimeToString(endDateTime);
		topicData.Title = TopicTitle.text;
		topicData.Content = Content.text;
		topicData.Type = CalendarType;
		StartCoroutine(CharacterCalendar.PutTopic(delegate
		{
			SingletonMonoBehaviour<AppUtility>.Instance.ShowDialogAndPop("完了確認", "トピックを編集しました。", delegate
			{
				CharacterCalendar.ClearCache();
				MyTopicDetail.MarkReload();
				SingletonMonoBehaviour<CalendarManager>.Instance.CalendarController.MarkReload();
				SingletonMonoBehaviour<CalendarManager>.Instance.DayListView.MyController.MarkReload();
				SingletonMonoBehaviour<CalendarManager>.Instance.TypedTopicListView.MarkReload();
				IsPosting = false;
			});
		}, delegate(UnityWebRequest result)
		{
			AppUtility.ShowErr(result.downloadHandler.text, "CalendarTopic", IsPop: false);
			IsPosting = false;
		}, topicData, LoadingAnimation.Default));
		EventSystem.current.SetSelectedGameObject(null);
	}
}
