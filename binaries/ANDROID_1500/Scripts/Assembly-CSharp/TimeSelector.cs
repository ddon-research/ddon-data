using System;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

[RequireComponent(typeof(Dropdown))]
public class TimeSelector : MonoBehaviour, IPointerDownHandler, IEventSystemHandler
{
	[Range(0f, 60f)]
	[SerializeField]
	private uint MinutesSpan;

	private Dropdown TimeDropDown;

	private void Start()
	{
	}

	public void ResetOptions(DateTime initDate)
	{
		if (TimeDropDown == null)
		{
			TimeDropDown = GetComponent<Dropdown>();
		}
		TimeDropDown.ClearOptions();
		int hour = initDate.Hour;
		int minute = initDate.Minute;
		int num = (int)(minute / MinutesSpan);
		minute = (int)(num * MinutesSpan);
		int num2 = minute / 60;
		minute %= 60;
		TimeDropDown.options.Add(new Dropdown.OptionData($"{hour + num2:00}:{minute:00}"));
		TimeDropDown.value = 0;
		TimeDropDown.RefreshShownValue();
	}

	public void ResetOptions()
	{
		ResetOptions(DateTime.Now);
	}

	public void SetTimeOptions()
	{
		if (TimeDropDown.options.Count > 2)
		{
			return;
		}
		DateTime value = GetValue();
		TimeDropDown.ClearOptions();
		bool flag = false;
		int num = 0;
		TimeDropDown.value = num;
		for (uint num2 = 0u; num2 < 24; num2++)
		{
			for (uint num3 = 0u; num3 < 60; num3 += MinutesSpan)
			{
				TimeDropDown.options.Add(new Dropdown.OptionData($"{num2:00}:{num3:00}"));
				num++;
				if (!flag && num2 == value.Hour && num3 == value.Minute)
				{
					TimeDropDown.value = num;
					flag = true;
				}
			}
		}
		TimeDropDown.RefreshShownValue();
	}

	public void OnPointerDown(PointerEventData evd)
	{
		SetTimeOptions();
	}

	public DateTime GetValue()
	{
		string text = TimeDropDown.captionText.text;
		string[] array = text.Split(':');
		int num = int.Parse(array[0]);
		int num2 = int.Parse(array[1]);
		return default(DateTime).AddHours(num).AddMinutes(num2);
	}
}
