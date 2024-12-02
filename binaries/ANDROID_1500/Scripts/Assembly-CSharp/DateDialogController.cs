using System;
using UnityEngine;
using UnityEngine.UI;

public class DateDialogController : SingletonMonoBehaviour<DateDialogController>
{
	[SerializeField]
	private GameObject Window;

	[SerializeField]
	private InputField Year;

	[SerializeField]
	private InputField Month;

	[SerializeField]
	private InputField Day;

	[SerializeField]
	private InputField Hour;

	[SerializeField]
	private InputField Minute;

	[SerializeField]
	private Text Header;

	[SerializeField]
	private Button OkButton;

	[SerializeField]
	private Slider HourSlider;

	[SerializeField]
	private Slider MinuteSlider;

	public void Start()
	{
		NavigationViewController.AddProhibit(Window);
	}

	public void ResetDate(DateTime date)
	{
		Year.text = date.Year.ToString();
		Month.text = date.Month.ToString();
		Day.text = date.Day.ToString();
		Hour.text = date.Hour.ToString();
		Minute.text = date.Minute.ToString();
		HourSlider.value = date.Hour;
		MinuteSlider.value = date.Minute;
	}

	public void ShowDialog(string message, DateTime date, Action<DateTime> callback = null)
	{
		NavigationViewController.AddProhibit(Window);
		Header.text = message;
		ResetDate(date);
		Window.SetActive(value: true);
		OkButton.onClick.RemoveAllListeners();
		OkButton.onClick.AddListener(delegate
		{
			int num = -1;
			int num2 = 0;
			int num3 = 0;
			int num4 = 0;
			int num5 = 0;
			DateTime obj;
			try
			{
				num = int.Parse(Year.text);
				num2 = int.Parse(Month.text);
				num3 = int.Parse(Day.text);
				num4 = int.Parse(Hour.text);
				num5 = int.Parse(Minute.text);
				obj = new DateTime(num, num2, num3, num4, num5, 0);
			}
			catch (Exception)
			{
				string text = "日時";
				if (num < 0)
				{
					text = "西暦";
				}
				else if (num2 < 1 || num2 > 12)
				{
					text = "月";
				}
				else if (num3 < 1 || num3 > 31)
				{
					text = "日";
				}
				else if (num4 < 0 || num4 > 23)
				{
					text = "時間";
				}
				else if (num5 < 0 || num5 > 59)
				{
					text = "分";
				}
				SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "エラー", text + "の指定が不正です。");
				return;
			}
			if (callback != null)
			{
				callback(obj);
			}
			Window.SetActive(value: false);
		});
	}

	public void ChangeHourSlider()
	{
		float value = HourSlider.value;
		Hour.text = value.ToString();
	}

	public void ChangeHourText()
	{
		try
		{
			int num = int.Parse(Hour.text);
			HourSlider.value = num;
		}
		catch (Exception)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "エラー", "時間の値が不正です。");
		}
	}

	public void ChangeMinuteSlider()
	{
		float value = MinuteSlider.value;
		Minute.text = value.ToString();
	}

	public void ChangeMinuteText()
	{
		try
		{
			int num = int.Parse(Minute.text);
			MinuteSlider.value = num;
		}
		catch (Exception)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "エラー", "分の値が不正です。");
		}
	}
}
