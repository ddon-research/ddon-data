using System;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class GameTimeController : MonoBehaviour
{
	[SerializeField]
	private Text DateTimeText;

	[SerializeField]
	private Image WeatherImage;

	[SerializeField]
	private List<Sprite> WeatherSplites;

	[SerializeField]
	private Text MoonText;

	private float TimeElapsed;

	private void Awake()
	{
		DateTimeText.gameObject.SetActive(value: false);
		WeatherImage.gameObject.SetActive(value: false);
		MoonText.gameObject.SetActive(value: false);
	}

	private void Start()
	{
		StartCoroutine(WebRequest.Environment.Get(delegate(Packet.Environment result)
		{
			GameDateTimeConverter.SetOriginalEarthTime((int)result.OriginalRealTimeYear, (int)result.OriginalRealTimeMon, (int)result.OriginalRealTimeMDay, (int)result.OriginalRealTimeHour);
			GameDateTimeConverter.SetOriginalGameTime(result.OriginalGameTimeYear, result.OriginalGameTimeMon, result.OriginalGameTimeMDay, result.OriginalGameTimeHour, 0uL, 0uL);
			GameDateTimeConverter.GameTimeOneDayMin = result.GameTimeOneDayMin;
			GameDateTimeConverter.WeatherLoopInfos = result.WeatherLoops;
			GameDateTimeConverter.MoonAgeLoopSec = result.MoonAgeLoopSec;
			DateTimeText.gameObject.SetActive(value: true);
			WeatherImage.gameObject.SetActive(value: true);
			MoonText.gameObject.SetActive(value: true);
			UpdateContent();
		}, null));
	}

	private void Update()
	{
		if (GameDateTimeConverter.GameTimeOneDayMin != 0)
		{
			TimeElapsed += Time.deltaTime;
			if (TimeElapsed > 1f)
			{
				UpdateContent();
				TimeElapsed = 0f;
			}
		}
	}

	private void UpdateContent()
	{
		GameDateTime gameDateTime = GameDateTimeConverter.EarthToGame(DateTime.Now);
		DateTimeText.text = gameDateTime.Hh.ToString("00") + ":" + gameDateTime.Nn.ToString("00");
		uint earthSecToWeather = GameDateTimeConverter.GetEarthSecToWeather(DateTime.Now);
		WeatherImage.sprite = WeatherSplites[(int)(earthSecToWeather - 1)];
		uint earthSecToMoonAge = GameDateTimeConverter.GetEarthSecToMoonAge(DateTime.Now);
		switch (earthSecToMoonAge)
		{
		case 0u:
			MoonText.text = "新月";
			break;
		case 1u:
		case 2u:
		case 3u:
		case 4u:
		case 5u:
		case 6u:
		case 7u:
		case 8u:
		case 9u:
		case 10u:
		case 11u:
		case 12u:
		case 13u:
		case 14u:
			MoonText.text = "上弦月";
			break;
		case 15u:
			MoonText.text = "満月";
			break;
		default:
			MoonText.text = "下弦月";
			break;
		}
		SingletonMonoBehaviour<HomeNpcManager>.Instance.SetEnvironment(gameDateTime, earthSecToWeather, earthSecToMoonAge);
	}
}
