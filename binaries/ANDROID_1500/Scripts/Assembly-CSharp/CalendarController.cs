using System;
using System.Collections;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.Networking;
using UnityEngine.UI;
using WebRequest;

public class CalendarController : MonoBehaviour
{
	public enum MARKER_FILTER_TYPE
	{
		NONE,
		ALL,
		BEGIN_AND_END,
		BEGIN_ONLY
	}

	private DateTime m_Date;

	private const uint TOTAL_DAY_SIZE = 42u;

	[SerializeField]
	private GameObject m_DayButtonPrefab;

	[SerializeField]
	private Text m_HeaderYear;

	[SerializeField]
	private Text m_HeaderMonth;

	[SerializeField]
	private GameObject m_CalendarGridPrefab;

	[SerializeField]
	private GameObject m_CalendarGrid;

	[SerializeField]
	private bool m_IsChangingMonth;

	[SerializeField]
	private bool IsLoadingAbstract;

	[SerializeField]
	private float m_TweenWaitTime = 0.5f;

	[SerializeField]
	private float m_TweenDistance = 30f;

	[SerializeField]
	private bool NeedReload;

	private IEnumerator routine;

	private void Start()
	{
		m_Date = DateTime.Now;
		GameObject grid = base.transform.FindChild("CalendarGrid").gameObject;
		SetCalendar(m_Date, grid);
	}

	private void Update()
	{
		if (NeedReload)
		{
			Reload();
			NeedReload = false;
		}
	}

	private bool CanChange()
	{
		return !m_IsChangingMonth && !IsLoadingAbstract;
	}

	public void Reload()
	{
		int year = int.Parse(m_HeaderYear.text);
		int month = int.Parse(m_HeaderMonth.text);
		DateTime date = new DateTime(year, month, 1);
		SetCalendar(date, m_CalendarGrid);
	}

	public void MarkReload()
	{
		NeedReload = true;
	}

	private void SetCalendar(DateTime date, GameObject grid)
	{
		uint year = (uint)DateTime.Now.Year;
		uint month = (uint)DateTime.Now.Month;
		uint day = (uint)DateTime.Now.Day;
		foreach (Transform componentInChild in grid.GetComponentInChildren<Transform>())
		{
			UnityEngine.Object.Destroy(componentInChild.gameObject);
		}
		m_HeaderYear.text = date.Year.ToString();
		m_HeaderMonth.text = date.Month.ToString();
		DateTime dateTime = new DateTime(date.Year, date.Month, 1);
		int num = DateTime.DaysInMonth(date.Year, date.Month);
		uint num2 = 0u;
		for (uint num3 = 0u; num3 < (uint)dateTime.DayOfWeek; num3++)
		{
			GameObject gameObject = UnityEngine.Object.Instantiate(m_DayButtonPrefab);
			gameObject.transform.SetParent(grid.transform);
			gameObject.transform.localScale = new Vector3(1f, 1f, 1f);
			num2++;
		}
		for (uint num4 = 0u; num4 < num; num4++)
		{
			GameObject gameObject2 = UnityEngine.Object.Instantiate(m_DayButtonPrefab);
			gameObject2.transform.SetParent(grid.transform);
			gameObject2.transform.localScale = new Vector3(1f, 1f, 1f);
			DayButton component = gameObject2.GetComponent<DayButton>();
			bool isToday = false;
			if (year == date.Year && month == date.Month && day == num4 + 1)
			{
				isToday = true;
			}
			DateTime date2 = dateTime.AddDays(num4);
			component.UpdateContent(date2, SingletonMonoBehaviour<CalendarManager>.Instance.DayListView, isToday);
			num2++;
		}
		for (uint num5 = num2; num5 < 42; num5++)
		{
			GameObject gameObject3 = UnityEngine.Object.Instantiate(m_DayButtonPrefab);
			gameObject3.transform.SetParent(grid.transform);
			gameObject3.transform.localScale = new Vector3(1f, 1f, 1f);
			num2++;
		}
		m_CalendarGrid = grid;
		SetScheduleMarker(date.Year, date.Month, grid.transform);
	}

	public void ChangeNextMonth()
	{
		if (CanChange())
		{
			m_IsChangingMonth = true;
			GameObject currentGrid = m_CalendarGrid;
			RectTransform rectTransform = currentGrid.transform as RectTransform;
			Vector2 vector = new Vector2(rectTransform.position.x + m_TweenDistance, rectTransform.position.y);
			Vector2 pos = new Vector2(rectTransform.anchoredPosition.x, rectTransform.anchoredPosition.y);
			GameObject gameObject = UnityEngine.Object.Instantiate(m_CalendarGridPrefab);
			gameObject.transform.SetParent(base.transform);
			gameObject.transform.position = vector;
			gameObject.name = "CalendarGrid";
			gameObject.transform.localScale = new Vector3(1f, 1f, 1f);
			m_Date = m_Date.AddMonths(1);
			SetCalendar(m_Date, gameObject);
			CanvasGroup component = currentGrid.GetComponent<CanvasGroup>();
			component.FadeTo(0f, m_TweenWaitTime, 0f, iTween.EaseType.easeOutSine, delegate
			{
				iTween.Stop(currentGrid.gameObject);
				UnityEngine.Object.Destroy(currentGrid.gameObject);
			});
			CanvasGroup component2 = gameObject.GetComponent<CanvasGroup>();
			component2.alpha = 0.3f;
			(gameObject.transform as RectTransform).MoveTo(pos, m_TweenWaitTime, 0f, iTween.EaseType.easeInSine, delegate
			{
			});
			component2.FadeTo(1f, m_TweenWaitTime, 0f, iTween.EaseType.easeInSine, delegate
			{
				m_IsChangingMonth = false;
			});
			if (EventSystem.current != null)
			{
				EventSystem.current.SetSelectedGameObject(null);
			}
		}
	}

	public void ChangePrevMonth()
	{
		if (CanChange())
		{
			m_IsChangingMonth = true;
			GameObject currentGrid = m_CalendarGrid;
			RectTransform rectTransform = currentGrid.transform as RectTransform;
			Vector2 vector = new Vector2(rectTransform.position.x - m_TweenDistance, rectTransform.position.y);
			Vector2 pos = new Vector2(rectTransform.anchoredPosition.x, rectTransform.anchoredPosition.y);
			GameObject gameObject = UnityEngine.Object.Instantiate(m_CalendarGridPrefab);
			gameObject.transform.SetParent(base.transform);
			gameObject.transform.position = vector;
			gameObject.name = "CalendarGrid";
			gameObject.transform.localScale = new Vector3(1f, 1f, 1f);
			m_Date = m_Date.AddMonths(-1);
			SetCalendar(m_Date, gameObject);
			CanvasGroup component = currentGrid.GetComponent<CanvasGroup>();
			component.FadeTo(0f, m_TweenWaitTime, 0f, iTween.EaseType.easeOutSine, delegate
			{
				iTween.Stop(currentGrid.gameObject);
				UnityEngine.Object.Destroy(currentGrid.gameObject);
			});
			CanvasGroup component2 = gameObject.GetComponent<CanvasGroup>();
			component2.alpha = 0.3f;
			(gameObject.transform as RectTransform).MoveTo(pos, m_TweenWaitTime, 0f, iTween.EaseType.easeInSine, delegate
			{
			});
			component2.FadeTo(1f, m_TweenWaitTime, 0f, iTween.EaseType.easeInSine, delegate
			{
				m_IsChangingMonth = false;
			});
			if (EventSystem.current != null)
			{
				EventSystem.current.SetSelectedGameObject(null);
			}
		}
	}

	private void SetScheduleMarker(int year, int month, Transform targetGrid)
	{
		IsLoadingAbstract = true;
		routine = CharacterCalendar.GetAbstract(delegate(CalendarAbstractParam result)
		{
			if (result == null)
			{
				CharacterCalendar.ClearCache_GetAbstractInt32Int32();
				IsLoadingAbstract = false;
			}
			else
			{
				routine = null;
				Dictionary<CalendarTopic.CALENDAR_TYPE, CalendarMarkerFilterData> filterList = SingletonMonoBehaviour<CalendarManager>.Instance.MarkerFilter.GetFilterList();
				DateTime date = new DateTime(year, month, 1);
				foreach (Transform componentInChild in targetGrid.GetComponentInChildren<Transform>())
				{
					DayButton component = componentInChild.GetComponent<DayButton>();
					component.CheckAbstract(date, result.abstList, filterList);
				}
				IsLoadingAbstract = false;
			}
		}, delegate(UnityWebRequest result)
		{
			routine = null;
			IsLoadingAbstract = false;
			AppUtility.ShowErr(result.downloadHandler.text, "CalendarAbstract", IsPop: false);
		}, year, month, CacheOption.OneHour);
		StartCoroutine(routine);
	}

	public void OnEnable()
	{
		if (routine != null)
		{
			StartCoroutine(routine);
		}
	}

	public void OfficialPush()
	{
		SingletonMonoBehaviour<CalendarManager>.Instance.TypedTopicListView.Push(CalendarTopic.CALENDAR_TYPE.EVENT);
	}

	public void PrivatePush()
	{
		SingletonMonoBehaviour<CalendarManager>.Instance.TypedTopicListView.Push(CalendarTopic.CALENDAR_TYPE.PRIVATE);
	}

	public void ClanPush()
	{
		SingletonMonoBehaviour<CalendarManager>.Instance.TypedTopicListView.Push(CalendarTopic.CALENDAR_TYPE.CLAN);
	}

	public void Push(ViewController page)
	{
		SingletonMonoBehaviour<NavigationViewController>.Instance.Push(page);
	}
}
