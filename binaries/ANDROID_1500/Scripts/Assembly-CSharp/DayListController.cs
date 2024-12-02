using System;
using System.Collections;
using Packet;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.Networking;
using UnityEngine.UI;
using WebRequest;

public class DayListController : TableViewController<CalendarTopic>
{
	[SerializeField]
	private float CellItemHeight = 90f;

	[SerializeField]
	private Text SelectDateYear;

	[SerializeField]
	private Text SelectDateDay;

	[SerializeField]
	private CanvasGroup MyCanvas;

	[SerializeField]
	private bool IsLoaded;

	[SerializeField]
	private RectTransform ContentHolder;

	[SerializeField]
	private float FadeTime = 0.3f;

	[SerializeField]
	private bool NeedReload;

	private IEnumerator routine;

	private DateTime LastUpdate;

	[SerializeField]
	private ReloadChecker MyReloadChecker;

	[SerializeField]
	protected bool IsGetting;

	protected object thisLock = new object();

	[SerializeField]
	private Text EmptyText;

	[SerializeField]
	public DateTime SelectDate { get; private set; }

	public void FirstInitPrepare()
	{
		TableData.Clear();
		for (int i = 0; i < 5; i++)
		{
			CalendarTopic calendarTopic = new CalendarTopic();
			calendarTopic.BeginDate = "1900-01-01T00:00:00+09:00";
			calendarTopic.EndDate = "1900-01-01T00:00:00+09:00";
			calendarTopic.Created = "1900-01-01T00:00:00+09:00";
			calendarTopic.ModifiedAt = "1900-01-01T00:00:00+09:00";
			calendarTopic.LikeUpdatedAt = "1900-01-01T00:00:00+09:00";
			calendarTopic.UpdatedAt = "1900-01-01T00:00:00+09:00";
			calendarTopic.Title = string.Empty;
			calendarTopic.Content = string.Empty;
			calendarTopic.TopicId = 0uL;
			CalendarTopic item = calendarTopic;
			TableData.Add(item);
		}
		UpdateContents();
		TableData.Clear();
	}

	public void UpdateContent(DateTime date)
	{
		SelectDate = new DateTime(date.Year, date.Month, date.Day);
		SelectDateYear.text = date.Year.ToString();
		SelectDateDay.text = date.ToString("MM.dd");
	}

	public void Init()
	{
		EmptyText.gameObject.SetActive(value: false);
		TableData.Clear();
		MyCanvas.alpha = 0f;
		MyReloadChecker.Init(delegate
		{
			CharacterCalendar.ClearCache();
			ReloadContent();
			MyReloadChecker.MarkHideReload();
		});
		LoadDataCore(0, delegate
		{
			MyCanvas.alpha = 1f;
			routine = UpdateCheck();
			StartCoroutine(routine);
		});
	}

	private void LoadDataCore(int offset, Action onComplete = null, LoadingAnimation anime = LoadingAnimation.None)
	{
		if (offset == 0)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
			MyReloadChecker.MarkHideReload();
		}
		NeedReload = false;
		EmptyText.gameObject.SetActive(value: true);
		StartCoroutine(CharacterCalendar.GetTopic(delegate(CalendarTopicParam result)
		{
			int num = 0;
			if (result.TopicList != null)
			{
				foreach (CalendarTopic topic in result.TopicList)
				{
					TableData.Add(topic);
					num++;
				}
				if (num == 0)
				{
					UpdateContents();
					if (TableData.Count == 0)
					{
						EmptyText.gameObject.SetActive(value: true);
					}
					else
					{
						EmptyText.gameObject.SetActive(value: false);
					}
					DateTime dateTime = default(DateTime);
					foreach (CalendarTopic tableDatum in TableData)
					{
						DateTime dateTime2 = DateTime.Parse(tableDatum.ModifiedAt);
						if (dateTime2.CompareTo(dateTime) > 0)
						{
							dateTime = dateTime2;
						}
					}
					LastUpdate = dateTime;
					MyReloadChecker.MarkHideReload();
					if (onComplete != null)
					{
						onComplete();
					}
					SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
				}
				else
				{
					LoadDataCore(num + offset, onComplete);
				}
			}
		}, delegate(UnityWebRequest result)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			AppUtility.ShowErr(result.downloadHandler.text, "CalendarTopic");
		}, "day_list", 5, SelectDate.Year, SelectDate.Month, SelectDate.Day, offset, CacheOption.OneHour, anime));
	}

	protected override float CellHeightAtIndex(int index)
	{
		return CellItemHeight;
	}

	protected override void Awake()
	{
		base.Awake();
	}

	protected override void Start()
	{
		base.Start();
	}

	public void Update()
	{
		if (NeedReload)
		{
			ReloadContent();
			NeedReload = false;
		}
	}

	public void MarkReload()
	{
		NeedReload = true;
	}

	public void ReloadContent()
	{
		TableData.Clear();
		MyCanvas.FadeTo(0f, FadeTime, 0f, iTween.EaseType.easeOutSine, delegate
		{
			LoadDataCore(0, delegate
			{
				MyCanvas.FadeTo(1f, FadeTime, 0f, iTween.EaseType.easeInSine, delegate
				{
					IsGetting = false;
				});
			});
		});
	}

	private void OnEnable()
	{
		if (!IsLoaded)
		{
			Init();
			IsLoaded = true;
		}
		if (routine != null)
		{
			StartCoroutine(routine);
		}
		IsGetting = false;
	}

	public override void OnNavigationPushEnd()
	{
		ContentHolder.localPosition = new Vector2(ContentHolder.localPosition.x, 0f);
	}

	public override void OnNavigationPopBegin()
	{
		IsLoaded = false;
		routine = null;
		ContentHolder.anchoredPosition = new Vector2(ContentHolder.anchoredPosition.x, 0f);
	}

	public TopicDetail GetTopicDetail(CalendarTopic.CALENDAR_TYPE type)
	{
		return type switch
		{
			CalendarTopic.CALENDAR_TYPE.PRIVATE => SingletonMonoBehaviour<CalendarManager>.Instance.PrivateTopicDetail, 
			CalendarTopic.CALENDAR_TYPE.CLAN => SingletonMonoBehaviour<CalendarManager>.Instance.ClanTopicDetail, 
			CalendarTopic.CALENDAR_TYPE.EVENT => SingletonMonoBehaviour<CalendarManager>.Instance.OfficialTopicDetail, 
			_ => null, 
		};
	}

	public void NextDayList()
	{
		lock (thisLock)
		{
			if (IsGetting)
			{
				return;
			}
			IsGetting = true;
		}
		UpdateContent(SelectDate.AddDays(1.0));
		ContentHolder.anchoredPosition = new Vector2(ContentHolder.anchoredPosition.x, 0f);
		ReloadContent();
		if (EventSystem.current != null)
		{
			EventSystem.current.SetSelectedGameObject(null);
		}
	}

	public void PrevDayList()
	{
		lock (thisLock)
		{
			if (IsGetting)
			{
				return;
			}
			IsGetting = true;
		}
		UpdateContent(SelectDate.AddDays(-1.0));
		ContentHolder.anchoredPosition = new Vector2(ContentHolder.anchoredPosition.x, 0f);
		ReloadContent();
		if (EventSystem.current != null)
		{
			EventSystem.current.SetSelectedGameObject(null);
		}
	}

	private IEnumerator UpdateCheck()
	{
		while (base.gameObject.activeInHierarchy)
		{
			StartCoroutine(CharacterCalendar.PostListUpdatedInfo(value: new CalendarUpdateInfo
			{
				Type = CalendarTopic.CALENDAR_TYPE.ALL,
				UpdateDate = CalendarTopic.DateTimeToString(LastUpdate),
				SelectDate = CalendarTopic.DateTimeToString(SelectDate)
			}, onResult: delegate(CalendarUpdateInfoListParam result)
			{
				if (result.infoList.Count > 0)
				{
					MyReloadChecker.MarkShowReload();
				}
				else
				{
					MyReloadChecker.MarkHideReload();
				}
			}, onError: delegate
			{
			}));
			yield return new WaitForSeconds(CalendarConstParams.RELOAD_INTERVAL);
		}
	}
}
