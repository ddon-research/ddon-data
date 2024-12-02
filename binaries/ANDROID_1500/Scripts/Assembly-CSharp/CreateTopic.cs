using System;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.Events;
using UnityEngine.Networking;
using UnityEngine.UI;
using WebRequest;

public class CreateTopic : ViewController
{
	public enum CREATE_FLOW_TYPE
	{
		TYPE_LIST,
		OFFICIAL_QUOTE,
		DAY_LIST
	}

	[SerializeField]
	protected CalendarTopic.CALENDAR_TYPE CalendarType;

	[SerializeField]
	protected InputField TopicTitle;

	[SerializeField]
	protected InputField Content;

	[SerializeField]
	protected GameObject CalTypePrivate;

	[SerializeField]
	protected GameObject CalTypeClan;

	[SerializeField]
	protected GameObject CalTypeClanBoard;

	[SerializeField]
	protected RectTransform ContentTrans;

	[SerializeField]
	protected RectTransform InputHolder;

	[SerializeField]
	protected Vector2 BodyOriginSize = Vector2.zero;

	[SerializeField]
	protected Vector2 BodyOriginPos = Vector2.zero;

	[SerializeField]
	protected ChildTextFitter MyChildTextFitter;

	[SerializeField]
	protected Text MyText;

	[SerializeField]
	protected GameObject TypeSelectButton;

	[SerializeField]
	protected Button TitleInputButton;

	[SerializeField]
	protected Button ContentInputButton;

	[SerializeField]
	protected bool IsPosting;

	protected object thisLock = new object();

	[SerializeField]
	protected RectTransform MaskObject;

	[SerializeField]
	protected Text StartDate;

	private DateTime _StartDateTime;

	[SerializeField]
	protected Text EndDate;

	private DateTime _EndDateTime;

	[SerializeField]
	protected CREATE_FLOW_TYPE flowType;

	protected DateTime StartDateTime
	{
		get
		{
			return _StartDateTime;
		}
		set
		{
			_StartDateTime = value;
			StartDate.text = DateToString(value);
		}
	}

	protected DateTime EndDateTime
	{
		get
		{
			return _EndDateTime;
		}
		set
		{
			_EndDateTime = value;
			EndDate.text = DateToString(value);
		}
	}

	protected void SetModifiedFlag()
	{
		base.IsPopBeginCheck = true;
	}

	public void OpenStartDateEdit()
	{
		SingletonMonoBehaviour<DateDialogController>.Instance.ShowDialog("開始時刻を登録してください", StartDateTime, delegate(DateTime result)
		{
			StartDateTime = result;
		});
		SetModifiedFlag();
	}

	public void OpenEndDateEdit()
	{
		SingletonMonoBehaviour<DateDialogController>.Instance.ShowDialog("終了時刻を登録してください", EndDateTime, delegate(DateTime result)
		{
			EndDateTime = result;
		});
		SetModifiedFlag();
	}

	protected void ResetFields(CalendarTopic.CALENDAR_TYPE type = CalendarTopic.CALENDAR_TYPE.NONE, float boardSize = 0f)
	{
		base.IsPopBeginCheck = false;
		if (BodyOriginSize == Vector2.zero)
		{
			RectTransform component = InputHolder.gameObject.GetComponent<RectTransform>();
			BodyOriginSize = component.sizeDelta;
			BodyOriginPos = ContentTrans.anchoredPosition;
		}
		RectTransform component2 = InputHolder.gameObject.GetComponent<RectTransform>();
		ContentTrans.anchoredPosition = BodyOriginPos;
		MaskObject.sizeDelta = BodyOriginSize;
		component2.sizeDelta = BodyOriginSize;
		IsPosting = false;
	}

	public void ResetPage(CalendarTopic.CALENDAR_TYPE type, CREATE_FLOW_TYPE fType = CREATE_FLOW_TYPE.TYPE_LIST)
	{
		ResetPage(type, fType, DateTime.Now);
	}

	public void ResetPage(CalendarTopic.CALENDAR_TYPE type, CREATE_FLOW_TYPE fType, DateTime selectedDate)
	{
		flowType = fType;
		CalendarType = type;
		TopicTitle.text = string.Empty;
		Content.text = string.Empty;
		ResetFields();
		StartDateTime = selectedDate;
		EndDateTime = selectedDate;
		SetCalendarTypeIcon();
	}

	public string DateToString(DateTime date)
	{
		string text = string.Empty;
		switch (date.DayOfWeek)
		{
		case DayOfWeek.Sunday:
			text = "(Sun)";
			break;
		case DayOfWeek.Monday:
			text = "(Mon)";
			break;
		case DayOfWeek.Tuesday:
			text = "(Tue)";
			break;
		case DayOfWeek.Wednesday:
			text = "(Wed)";
			break;
		case DayOfWeek.Thursday:
			text = "(Thu)";
			break;
		case DayOfWeek.Friday:
			text = "(Fri)";
			break;
		case DayOfWeek.Saturday:
			text = "(Sat)";
			break;
		}
		return date.ToString("yyyy-MM-dd ") + text + "  " + date.ToString("HH:mm");
	}

	public string DateToString(string date)
	{
		DateTime date2 = DateTime.Parse(date);
		return DateToString(date2);
	}

	public void UpdateContent(CalendarTopic.CALENDAR_TYPE type, CalendarTopic topicData)
	{
		ResetFields();
		flowType = CREATE_FLOW_TYPE.OFFICIAL_QUOTE;
		CalendarType = type;
		TopicTitle.text = topicData.Title;
		Content.text = topicData.Content;
		MyText.text = topicData.Content;
		MyChildTextFitter.Fitting();
		DateTime startDateTime = DateTime.Parse(topicData.BeginDate);
		DateTime endDateTime = DateTime.Parse(topicData.EndDate);
		StartDateTime = startDateTime;
		EndDateTime = endDateTime;
		SetCalendarTypeIcon();
	}

	protected void SetCalendarTypeIcon()
	{
		CalTypePrivate.SetActive(value: false);
		CalTypeClan.SetActive(value: false);
		if (TypeSelectButton != null)
		{
			TypeSelectButton.SetActive(value: false);
		}
		if (CalTypeClanBoard != null)
		{
			CalTypeClanBoard.SetActive(value: false);
		}
		switch (CalendarType)
		{
		case CalendarTopic.CALENDAR_TYPE.PRIVATE:
			CalTypePrivate.SetActive(value: true);
			return;
		case CalendarTopic.CALENDAR_TYPE.CLAN:
			CalTypeClan.SetActive(value: true);
			return;
		case CalendarTopic.CALENDAR_TYPE.CLAN_MESSAGE_BOARD:
			if (CalTypeClanBoard != null)
			{
				CalTypeClanBoard.SetActive(value: true);
			}
			return;
		}
		CalendarType = CalendarTopic.CALENDAR_TYPE.NONE;
		if (TypeSelectButton != null)
		{
			TypeSelectButton.SetActive(value: true);
		}
	}

	public void SelectTopicType()
	{
		List<CustomMenuContentData> list = new List<CustomMenuContentData>();
		list.Add(new CustomMenuContentData
		{
			Name = "プライベートトピック",
			OnClick = delegate
			{
				CalendarType = CalendarTopic.CALENDAR_TYPE.PRIVATE;
				SetCalendarTypeIcon();
				SetModifiedFlag();
			}
		});
		list.Add(new CustomMenuContentData
		{
			Name = "クラントピック",
			OnClick = delegate
			{
				CalendarType = CalendarTopic.CALENDAR_TYPE.CLAN;
				SetCalendarTypeIcon();
				SetModifiedFlag();
			}
		});
		SingletonMonoBehaviour<PopUpMenuController>.Instance.Show(list);
	}

	public override void OnNavigationPushEnd()
	{
	}

	public override void OnNavigationPopBegin()
	{
	}

	protected DateTime GetStartDateTime()
	{
		return StartDateTime;
	}

	protected DateTime GetEndDateTime()
	{
		return EndDateTime;
	}

	public bool CheckData()
	{
		if (TopicTitle.text.Length == 0)
		{
			Debug.Log("投稿エラー：タイトルが入力されていない。");
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "投稿エラー", "タイトルを入力してください。");
			return false;
		}
		if (TopicTitle.text.Length > 50)
		{
			Debug.Log("投稿エラー：タイトルが長すぎる。");
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "投稿エラー", "タイトルが最大文字数を超えています。\n50文字以下にしてください。\n(現在：" + TopicTitle.text.Length + "文字）");
			return false;
		}
		if (Content.text.Length == 0)
		{
			Debug.Log("投稿エラー：内容が入力されていない。");
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "投稿エラー", "本文を入力してください。");
			return false;
		}
		if (Content.text.Length > 300)
		{
			Debug.Log("投稿エラー：内容が長すぎる。");
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "投稿エラー", "本文が最大文字数を超えています。300文字以下にしてください。\n(現在：" + Content.text.Length + "文字）");
			return false;
		}
		DateTime startDateTime = GetStartDateTime();
		DateTime endDateTime = GetEndDateTime();
		if (startDateTime.CompareTo(endDateTime) > 0)
		{
			Debug.Log("投稿エラー：開始日時が終了日時よりも未来。");
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "投稿エラー", "終了は開始より後の日時を\n設定してください。");
			return false;
		}
		if (CalendarType != CalendarTopic.CALENDAR_TYPE.PRIVATE && CalendarType != CalendarTopic.CALENDAR_TYPE.CLAN && CalendarType != CalendarTopic.CALENDAR_TYPE.CLAN_MESSAGE_BOARD)
		{
			Debug.Log("投稿エラー：カレンダータイプが不正。");
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "投稿エラー", "トピックタイプが選択されていません。");
			return false;
		}
		return true;
	}

	public virtual void PostData()
	{
		if (!CheckData())
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
		CalendarTopic calendarTopic = new CalendarTopic();
		calendarTopic.BeginDate = CalendarTopic.DateTimeToString(startDateTime);
		calendarTopic.EndDate = CalendarTopic.DateTimeToString(endDateTime);
		calendarTopic.Title = TopicTitle.text;
		calendarTopic.Content = Content.text;
		calendarTopic.Type = CalendarType;
		StartCoroutine(CharacterCalendar.PostTopic(delegate
		{
			CharacterCalendar.ClearCache();
			switch (flowType)
			{
			case CREATE_FLOW_TYPE.TYPE_LIST:
				SingletonMonoBehaviour<CalendarManager>.Instance.TypedTopicListView.MarkReload();
				SingletonMonoBehaviour<AppUtility>.Instance.ShowDialogAndPop("完了確認", "トピックを作成しました。");
				break;
			case CREATE_FLOW_TYPE.OFFICIAL_QUOTE:
			case CREATE_FLOW_TYPE.DAY_LIST:
				SingletonMonoBehaviour<NavigationViewController>.Instance.AllPop();
				SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "完了確認", "トピックを作成しました。", delegate(ModalDialog.Result res)
				{
					if (res == ModalDialog.Result.OK)
					{
						SingletonMonoBehaviour<CalendarManager>.Instance.TypedTopicListView.Push(CalendarType);
						IsPosting = false;
					}
				});
				break;
			}
			SingletonMonoBehaviour<CalendarManager>.Instance.CalendarController.MarkReload();
			SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.MarkReload();
		}, delegate(UnityWebRequest result)
		{
			IsPosting = false;
			AppUtility.ShowErr(result.downloadHandler.text, "CalendarTopic", IsPop: false);
			IsPosting = false;
		}, "topic", calendarTopic, LoadingAnimation.Default));
		EventSystem.current.SetSelectedGameObject(null);
	}

	public void ActivateTitleInputField()
	{
		TopicTitle.ActivateInputField();
		UnityEvent unityEvent = new UnityEvent();
		unityEvent.Invoke();
		SetModifiedFlag();
	}

	public void ActivateContentInputField()
	{
		MyChildTextFitter.Fitting();
		Content.ActivateInputField();
		UnityEvent unityEvent = new UnityEvent();
		unityEvent.Invoke();
		SetModifiedFlag();
	}
}
