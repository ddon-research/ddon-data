using System.Collections.Generic;
using Packet;
using UnityEngine;

public class CalendarMarkerFilter : ViewController
{
	[SerializeField]
	private CalendarMarkerFilterItem PrivateFilter;

	[SerializeField]
	private CalendarMarkerFilterItem ClanFilter;

	[SerializeField]
	private CalendarMarkerFilterItem OfficialFilter;

	private Dictionary<CalendarTopic.CALENDAR_TYPE, CalendarMarkerFilterData> CurrentFilterData;

	private void Start()
	{
	}

	public void FilterInit()
	{
		CalendarMarkerFilterPackage calendarMarkerFilter = PlayerPerfManager.GetCalendarMarkerFilter();
		if (calendarMarkerFilter == null || calendarMarkerFilter.filters == null || calendarMarkerFilter.filters.Count == 0)
		{
			PrivateFilter.UpdateContent(isOn: true, CalendarController.MARKER_FILTER_TYPE.BEGIN_AND_END);
			ClanFilter.UpdateContent(isOn: true, CalendarController.MARKER_FILTER_TYPE.BEGIN_AND_END);
			OfficialFilter.UpdateContent(isOn: true, CalendarController.MARKER_FILTER_TYPE.BEGIN_AND_END);
			CurrentFilterData = GetFilterListCore();
			return;
		}
		foreach (CalendarMarkerFilterData filter in calendarMarkerFilter.filters)
		{
			switch (filter.CalType)
			{
			case CalendarTopic.CALENDAR_TYPE.PRIVATE:
				PrivateFilter.UpdateContent(filter.IsEnable, filter.FilterType);
				break;
			case CalendarTopic.CALENDAR_TYPE.CLAN:
				ClanFilter.UpdateContent(filter.IsEnable, filter.FilterType);
				break;
			case CalendarTopic.CALENDAR_TYPE.EVENT:
				OfficialFilter.UpdateContent(filter.IsEnable, filter.FilterType);
				break;
			}
		}
		CurrentFilterData = GetFilterListCore();
	}

	public Dictionary<CalendarTopic.CALENDAR_TYPE, CalendarMarkerFilterData> GetFilterList()
	{
		return CurrentFilterData;
	}

	private Dictionary<CalendarTopic.CALENDAR_TYPE, CalendarMarkerFilterData> GetFilterListCore()
	{
		Dictionary<CalendarTopic.CALENDAR_TYPE, CalendarMarkerFilterData> dictionary = new Dictionary<CalendarTopic.CALENDAR_TYPE, CalendarMarkerFilterData>();
		dictionary[CalendarTopic.CALENDAR_TYPE.PRIVATE] = GetFilterData(CalendarTopic.CALENDAR_TYPE.PRIVATE);
		dictionary[CalendarTopic.CALENDAR_TYPE.CLAN] = GetFilterData(CalendarTopic.CALENDAR_TYPE.CLAN);
		dictionary[CalendarTopic.CALENDAR_TYPE.EVENT] = GetFilterData(CalendarTopic.CALENDAR_TYPE.EVENT);
		return dictionary;
	}

	private CalendarMarkerFilterData GetFilterData(CalendarTopic.CALENDAR_TYPE type)
	{
		bool isEnable = false;
		CalendarController.MARKER_FILTER_TYPE filterType = CalendarController.MARKER_FILTER_TYPE.BEGIN_ONLY;
		switch (type)
		{
		case CalendarTopic.CALENDAR_TYPE.PRIVATE:
			isEnable = PrivateFilter.GetEnable();
			filterType = PrivateFilter.GetFilterType();
			break;
		case CalendarTopic.CALENDAR_TYPE.CLAN:
			isEnable = ClanFilter.GetEnable();
			filterType = ClanFilter.GetFilterType();
			break;
		case CalendarTopic.CALENDAR_TYPE.EVENT:
			isEnable = OfficialFilter.GetEnable();
			filterType = OfficialFilter.GetFilterType();
			break;
		}
		CalendarMarkerFilterData calendarMarkerFilterData = new CalendarMarkerFilterData();
		calendarMarkerFilterData.IsEnable = isEnable;
		calendarMarkerFilterData.FilterType = filterType;
		calendarMarkerFilterData.CalType = type;
		return calendarMarkerFilterData;
	}

	public void OnSave()
	{
		CurrentFilterData = GetFilterListCore();
		CalendarMarkerFilterData item = CurrentFilterData[CalendarTopic.CALENDAR_TYPE.PRIVATE];
		CalendarMarkerFilterData item2 = CurrentFilterData[CalendarTopic.CALENDAR_TYPE.CLAN];
		CalendarMarkerFilterData item3 = CurrentFilterData[CalendarTopic.CALENDAR_TYPE.EVENT];
		List<CalendarMarkerFilterData> list = new List<CalendarMarkerFilterData>();
		list.Add(item);
		list.Add(item2);
		list.Add(item3);
		List<CalendarMarkerFilterData> filters = list;
		CalendarMarkerFilterPackage calendarMarkerFilterPackage = new CalendarMarkerFilterPackage();
		calendarMarkerFilterPackage.filters = filters;
		CalendarMarkerFilterPackage calendarMarkerFilter = calendarMarkerFilterPackage;
		PlayerPerfManager.SetCalendarMarkerFilter(calendarMarkerFilter);
		SingletonMonoBehaviour<AppUtility>.Instance.ShowDialogAndPop("確認", "マーカーの表示設定を保存しました。");
		SingletonMonoBehaviour<CalendarManager>.Instance.CalendarController.MarkReload();
	}

	public override void OnNavigationPushEnd()
	{
		base.IsPopBeginCheck = false;
	}

	public void OnValueChange()
	{
		base.IsPopBeginCheck = true;
	}

	public override void OnNavigationPopBegin()
	{
		if (CurrentFilterData == null)
		{
			return;
		}
		foreach (KeyValuePair<CalendarTopic.CALENDAR_TYPE, CalendarMarkerFilterData> currentFilterDatum in CurrentFilterData)
		{
			switch (currentFilterDatum.Key)
			{
			case CalendarTopic.CALENDAR_TYPE.PRIVATE:
				PrivateFilter.UpdateContent(currentFilterDatum.Value.IsEnable, currentFilterDatum.Value.FilterType);
				break;
			case CalendarTopic.CALENDAR_TYPE.CLAN:
				ClanFilter.UpdateContent(currentFilterDatum.Value.IsEnable, currentFilterDatum.Value.FilterType);
				break;
			case CalendarTopic.CALENDAR_TYPE.EVENT:
				OfficialFilter.UpdateContent(currentFilterDatum.Value.IsEnable, currentFilterDatum.Value.FilterType);
				break;
			}
		}
	}
}
