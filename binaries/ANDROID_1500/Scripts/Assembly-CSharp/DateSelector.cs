using System;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

[RequireComponent(typeof(Dropdown))]
public class DateSelector : MonoBehaviour, IPointerDownHandler, IEventSystemHandler
{
	[SerializeField]
	private uint DayRange;

	private Dropdown DateDropDown;

	private void Start()
	{
	}

	public void ResetOptions(DateTime initDate)
	{
		if (DateDropDown == null)
		{
			DateDropDown = GetComponent<Dropdown>();
		}
		DateDropDown.ClearOptions();
		DateTime dateTime = initDate;
		DateDropDown.options.Add(new Dropdown.OptionData(dateTime.ToString("yyyy-MM-dd")));
		DateDropDown.value = 0;
		DateDropDown.RefreshShownValue();
	}

	public void ResetOptions()
	{
		ResetOptions(DateTime.Now);
	}

	public void SetDateOptions()
	{
		if (DateDropDown.options.Count > 2)
		{
			return;
		}
		DateTime value = GetValue();
		DateTime dateTime = value.AddDays((0L - (long)DayRange) / 2);
		DateDropDown.ClearOptions();
		bool flag = false;
		DateDropDown.options.Add(new Dropdown.OptionData(dateTime.ToString("yyyy-MM-dd")));
		DateDropDown.value = 0;
		for (int i = 1; i < DayRange; i++)
		{
			dateTime = dateTime.AddDays(1.0);
			DateDropDown.options.Add(new Dropdown.OptionData(dateTime.ToString("yyyy-MM-dd")));
			if (!flag && dateTime.Year == value.Year && dateTime.Month == value.Month && dateTime.Day == value.Day)
			{
				DateDropDown.value = i;
				flag = true;
			}
		}
		DateDropDown.RefreshShownValue();
	}

	public void OnPointerDown(PointerEventData evd)
	{
		SetDateOptions();
	}

	public DateTime GetValue()
	{
		string text = DateDropDown.captionText.text;
		return DateTime.Parse(text);
	}
}
