using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;

public class CalendarMarkerFilterItem : MonoBehaviour
{
	[SerializeField]
	private Slider MySlider;

	[SerializeField]
	private Text FilterExplain;

	[SerializeField]
	private GameObject BlackFade;

	[SerializeField]
	private CalendarController.MARKER_FILTER_TYPE FilterType;

	private Dictionary<CalendarController.MARKER_FILTER_TYPE, string> FilterName = new Dictionary<CalendarController.MARKER_FILTER_TYPE, string>();

	[SerializeField]
	private UnityEvent OnValueChangeCallback;

	private void Start()
	{
		CalendarInit();
	}

	private void CalendarInit()
	{
		if (FilterName.Count == 0)
		{
			FilterName[CalendarController.MARKER_FILTER_TYPE.BEGIN_AND_END] = "開始日と終了日のみ";
			FilterName[CalendarController.MARKER_FILTER_TYPE.ALL] = "開始日から終了日まで全て";
			FilterName[CalendarController.MARKER_FILTER_TYPE.BEGIN_ONLY] = "開始日のみ";
			SetFilterType(FilterType);
		}
	}

	public void UpdateContent(bool isOn, CalendarController.MARKER_FILTER_TYPE type)
	{
		CalendarInit();
		MySlider.value = 0f;
		if (isOn)
		{
			MySlider.value = 1f;
		}
		SetFilterType(type);
	}

	public CalendarController.MARKER_FILTER_TYPE GetFilterType()
	{
		return FilterType;
	}

	public bool GetEnable()
	{
		return MySlider.value == 1f;
	}

	public void OnClick()
	{
		if (GetEnable())
		{
			List<CustomMenuContentData> list = new List<CustomMenuContentData>();
			list.Add(new CustomMenuContentData
			{
				Name = FilterName[CalendarController.MARKER_FILTER_TYPE.BEGIN_AND_END],
				OnClick = delegate
				{
					SetFilterType(CalendarController.MARKER_FILTER_TYPE.BEGIN_AND_END);
				}
			});
			list.Add(new CustomMenuContentData
			{
				Name = FilterName[CalendarController.MARKER_FILTER_TYPE.ALL],
				OnClick = delegate
				{
					SetFilterType(CalendarController.MARKER_FILTER_TYPE.ALL);
				}
			});
			list.Add(new CustomMenuContentData
			{
				Name = FilterName[CalendarController.MARKER_FILTER_TYPE.BEGIN_ONLY],
				OnClick = delegate
				{
					SetFilterType(CalendarController.MARKER_FILTER_TYPE.BEGIN_ONLY);
				}
			});
			SingletonMonoBehaviour<PopUpMenuController>.Instance.Show(list);
		}
	}

	public void SetFilterType(CalendarController.MARKER_FILTER_TYPE type)
	{
		OnValueChangeCallback.Invoke();
		FilterType = CalendarController.MARKER_FILTER_TYPE.BEGIN_ONLY;
		FilterExplain.text = FilterName[FilterType];
		if (FilterName.ContainsKey(type))
		{
			FilterType = type;
			FilterExplain.text = FilterName[FilterType];
		}
	}

	public void OnValueChange()
	{
		OnValueChangeCallback.Invoke();
		if (GetEnable())
		{
			BlackFade.SetActive(value: false);
		}
		else
		{
			BlackFade.SetActive(value: true);
		}
	}
}
