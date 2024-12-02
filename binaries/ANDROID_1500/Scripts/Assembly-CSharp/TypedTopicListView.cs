using System;
using System.Collections;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using WebRequest;

public class TypedTopicListView : ViewController
{
	[SerializeField]
	private TypedTopicListController ActiveList;

	[SerializeField]
	private TypedTopicListController DeadList;

	[SerializeField]
	private CalendarTopic.CALENDAR_TYPE m_Type;

	[SerializeField]
	private Text m_NumHeader;

	[SerializeField]
	private ListChangeTab ChangeTab;

	[SerializeField]
	private bool IsLoaded;

	[SerializeField]
	private bool NeedReload;

	[SerializeField]
	private GameObject PrivateIcon;

	[SerializeField]
	private GameObject ClanIcon;

	[SerializeField]
	private GameObject OfficialIcon;

	[SerializeField]
	private Text HeaderText;

	[SerializeField]
	private GameObject PrivateControll;

	[SerializeField]
	private GameObject ClanControll;

	[SerializeField]
	private GameObject OfficialControll;

	[SerializeField]
	private Text ActiveNum;

	private uint ActiveCounter;

	[SerializeField]
	private Text DeadNum;

	private uint DeadCounter;

	[SerializeField]
	private CanvasGroup ActiveCanvasGroup;

	[SerializeField]
	private CanvasGroup DeadCanvasGroup;

	private DateTime LastUpdate;

	private IEnumerator routine;

	private void Start()
	{
	}

	public void ChangeList(bool IsActiveList)
	{
		ActiveList.gameObject.SetActive(value: false);
		DeadList.gameObject.SetActive(value: false);
		if (IsActiveList)
		{
			ActiveList.gameObject.SetActive(value: true);
		}
		else
		{
			DeadList.gameObject.SetActive(value: true);
		}
	}

	public override void OnNavigationPushEnd()
	{
		ActiveList.OnNavigationPushEnd();
		DeadList.OnNavigationPushEnd();
	}

	public override void OnNavigationPopBegin()
	{
		ActiveList.OnNavigationPopBegin();
		DeadList.OnNavigationPopBegin();
		IsLoaded = false;
		routine = null;
		m_NumHeader.text = string.Empty;
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

	public void ReloadContent(Action callback = null)
	{
		ActiveList.TableClear();
		DeadList.TableClear();
		SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.MarkReload();
		LoadData(0, CacheOption.OneHour, callback);
	}

	private void OnEnable()
	{
		InitLoad();
		if (routine != null)
		{
			StartCoroutine(routine);
			routine = null;
		}
	}

	public void Push(CalendarTopic.CALENDAR_TYPE type)
	{
		Init(type);
		SingletonMonoBehaviour<NavigationViewController>.Instance.Push(this);
	}

	public void FirstInitPrepare()
	{
		ActiveList.TableClear();
		DeadList.TableClear();
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
			CalendarTopic topic = calendarTopic;
			ActiveList.TableAdd(topic);
			DeadList.TableAdd(topic);
		}
		ActiveList.SetUpdateContents();
		DeadList.SetUpdateContents();
		ActiveList.TableClear();
		DeadList.TableClear();
	}

	public void Init(CalendarTopic.CALENDAR_TYPE type)
	{
		NeedReload = false;
		m_Type = type;
		ChangeUIByType(type);
		ActiveList.Init(delegate
		{
			CharacterCalendar.ClearCache();
			ReloadContent();
		});
		DeadList.Init(delegate
		{
			CharacterCalendar.ClearCache();
			ReloadContent();
		});
	}

	private void InitLoad()
	{
		if (IsLoaded)
		{
			return;
		}
		ChangeTab.SetCallback(delegate
		{
			ChangeList(IsActiveList: true);
		}, delegate
		{
			ChangeList(IsActiveList: false);
		});
		LoadData(0, CacheOption.OneHour, delegate
		{
			ChangeTab.ChangeLeft();
			if (m_Type != CalendarTopic.CALENDAR_TYPE.PRIVATE)
			{
				routine = UpdateCheck();
				StartCoroutine(routine);
			}
		}, LoadingAnimation.Default);
		IsLoaded = true;
	}

	public bool ChangeUIByType(CalendarTopic.CALENDAR_TYPE type)
	{
		PrivateIcon.SetActive(value: false);
		ClanIcon.SetActive(value: false);
		OfficialIcon.SetActive(value: false);
		PrivateControll.SetActive(value: false);
		ClanControll.SetActive(value: false);
		OfficialControll.SetActive(value: false);
		GameObject gameObject = null;
		string text = string.Empty;
		switch (type)
		{
		case CalendarTopic.CALENDAR_TYPE.PRIVATE:
			gameObject = PrivateIcon;
			text = "プライベート トピック";
			PrivateControll.SetActive(value: true);
			break;
		case CalendarTopic.CALENDAR_TYPE.CLAN:
			gameObject = ClanIcon;
			text = "クラン トピック";
			ClanControll.SetActive(value: true);
			break;
		case CalendarTopic.CALENDAR_TYPE.EVENT:
			gameObject = OfficialIcon;
			text = "公式ニュース";
			OfficialControll.SetActive(value: true);
			break;
		}
		if (gameObject == null)
		{
			SingletonMonoBehaviour<AppUtility>.Instance.ShowDialogAndPop("致命的なエラー", "致命的なエラーが発生しました。");
			return false;
		}
		gameObject.SetActive(value: true);
		HeaderText.text = text;
		return true;
	}

	private void LoadData(int offset, CacheOption option, Action onComplete = null, LoadingAnimation anime = LoadingAnimation.None)
	{
		if (!base.gameObject.activeInHierarchy)
		{
			return;
		}
		if (offset == 0)
		{
			ActiveCounter = 0u;
			DeadCounter = 0u;
			ActiveList.TableClear();
			DeadList.TableClear();
			ActiveCanvasGroup.alpha = 0f;
			DeadCanvasGroup.alpha = 0f;
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		StartCoroutine(CharacterCalendar.GetTopic(delegate(CalendarTopicParam result)
		{
			int num = 0;
			if (result == null || result.TopicList == null)
			{
				ActiveList.MarkShowReload(flag: false);
				DeadList.MarkShowReload(flag: false);
				SingletonMonoBehaviour<AppUtility>.Instance.ShowDialogAndPop("エラー", "クラントピックの取得に失敗しました");
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
				CharacterCalendar.ClearCache_GetTopicStringInt32Int32Int32Int32Int32();
			}
			else
			{
				foreach (CalendarTopic topic in result.TopicList)
				{
					if (IsActive(topic))
					{
						ActiveList.TableAdd(topic);
						ActiveCounter++;
					}
					else
					{
						DeadList.TableAdd(topic);
						DeadCounter++;
					}
					num++;
				}
				if (num == 0)
				{
					m_NumHeader.text = string.Empty;
					CalendarTopic.CALENDAR_TYPE type = m_Type;
					if (type == CalendarTopic.CALENDAR_TYPE.CLAN || type == CalendarTopic.CALENDAR_TYPE.PRIVATE)
					{
						m_NumHeader.text = num + offset + "/" + result.TopicSizeMax;
					}
					DateTime dateTime = default(DateTime);
					List<CalendarTopic> tableList = ActiveList.GetTableList();
					foreach (CalendarTopic item in tableList)
					{
						DateTime dateTime2 = DateTime.Parse(item.ModifiedAt);
						if (dateTime2.CompareTo(dateTime) > 0)
						{
							dateTime = dateTime2;
						}
					}
					List<CalendarTopic> tableList2 = DeadList.GetTableList();
					foreach (CalendarTopic item2 in tableList2)
					{
						DateTime dateTime3 = DateTime.Parse(item2.ModifiedAt);
						if (dateTime3.CompareTo(dateTime) > 0)
						{
							dateTime = dateTime3;
						}
					}
					LastUpdate = dateTime;
					ActiveList.MarkShowReload(flag: false);
					DeadList.MarkShowReload(flag: false);
					SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.UpdateUpdateInfo(delegate
					{
						ActiveList.SetUpdateContents();
						DeadList.SetUpdateContents();
						ActiveCanvasGroup.alpha = 1f;
						DeadCanvasGroup.alpha = 1f;
						ActiveNum.text = ActiveCounter.ToString();
						DeadNum.text = DeadCounter.ToString();
						if (onComplete != null)
						{
							onComplete();
						}
						SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
					});
				}
				else
				{
					LoadData(num + offset, option, onComplete);
				}
			}
		}, delegate(UnityWebRequest result)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			AppUtility.ShowErr(result.downloadHandler.text, "CalendarTopic");
		}, "type_list", (int)m_Type, 1, 2, 3, offset, option, anime));
	}

	public void OpenCreateTopic()
	{
		SingletonMonoBehaviour<CalendarManager>.Instance.CreateTopic.ResetPage(m_Type);
		SingletonMonoBehaviour<NavigationViewController>.Instance.Push(SingletonMonoBehaviour<CalendarManager>.Instance.CreateTopic);
	}

	private IEnumerator UpdateCheck()
	{
		while (base.gameObject.activeInHierarchy)
		{
			StartCoroutine(CharacterCalendar.PostListUpdatedInfo(value: new CalendarUpdateInfo
			{
				Type = m_Type,
				UpdateDate = CalendarTopic.DateTimeToString(LastUpdate)
			}, onResult: delegate(CalendarUpdateInfoListParam result)
			{
				if (result.infoList.Count > 0)
				{
					ActiveList.MarkShowReload(flag: true);
					DeadList.MarkShowReload(flag: true);
				}
				else
				{
					ActiveList.MarkShowReload(flag: false);
					DeadList.MarkShowReload(flag: false);
				}
			}, onError: delegate
			{
			}));
			yield return new WaitForSeconds(CalendarConstParams.RELOAD_INTERVAL);
		}
	}

	public void OnClickAllRead()
	{
		foreach (CalendarTopic table in ActiveList.GetTableList())
		{
			CalendarUpdateInfo calendarUpdateInfo = new CalendarUpdateInfo();
			calendarUpdateInfo.CalendarId = table.CalendarId;
			calendarUpdateInfo.TopicId = table.TopicId;
			calendarUpdateInfo.Type = table.Type;
			calendarUpdateInfo.UpdateDate = table.ModifiedAt;
			CalendarUpdateInfo info = calendarUpdateInfo;
			SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.ReadTopic(info);
		}
		ReloadContent();
	}

	private bool IsActive(CalendarTopic topic)
	{
		return DateTime.Parse(topic.EndDate).CompareTo(DateTime.Now) > 0;
	}

	private int GetIndexList(CalendarTopic topic, List<CalendarTopic> list)
	{
		return list.FindIndex((CalendarTopic elem) => elem.TopicId == topic.TopicId && elem.CalendarId == topic.CalendarId && elem.Type == topic.Type);
	}

	public CalendarTopic GetSelectTopic(CalendarTopic topic, bool isNext)
	{
		int num = -1;
		List<CalendarTopic> tableList = DeadList.GetTableList();
		if (IsActive(topic))
		{
			tableList = ActiveList.GetTableList();
		}
		num = GetIndexList(topic, tableList);
		if (num < 0 || num >= tableList.Count)
		{
			return null;
		}
		int index = (tableList.Count + num - 1) % tableList.Count;
		if (isNext)
		{
			index = (tableList.Count + num + 1) % tableList.Count;
		}
		return tableList[index];
	}
}
