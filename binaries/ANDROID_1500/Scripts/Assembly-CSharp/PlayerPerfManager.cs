using System;
using UnityEngine;

public static class PlayerPerfManager
{
	private const string K_UUID = "ddo_uuid";

	private const string K_IS_READ_TITLE_INTRODUCTION = "ddo_is_read_title_introduction";

	private const string K_COGID = "ddo_cogid";

	private const string K_API_TOKEN = "ddo_api_token";

	private const string K_READ_TOS_VERSION = "ddo_read_tos_version";

	private const string K_CAL_MARK_FILTER = "ddo_calendar_filter";

	private const string K_CAL_BG_IMAGE = "ddo_calendar_bg_image";

	private const string K_CAL_READ_TOPIC = "ddo_calendar_read_topic";

	public static string GetUUID()
	{
		string text = PlayerPrefs.GetString("ddo_uuid");
		if (string.IsNullOrEmpty(text))
		{
			text = Guid.NewGuid().ToString().Replace("-", string.Empty);
			PlayerPrefs.SetString("ddo_uuid", text);
			PlayerPrefs.Save();
			Debug.Log("Generated UUID. " + text);
		}
		return text;
	}

	public static void SetIsReadTitleIntroduction(bool b)
	{
		PlayerPrefs.SetInt("ddo_is_read_title_introduction", b ? 1 : 0);
		PlayerPrefs.Save();
	}

	public static bool GetIsReadTitleIntroduction()
	{
		return PlayerPrefs.GetInt("ddo_is_read_title_introduction") == 1;
	}

	public static void SetCogID(string id)
	{
		PlayerPrefs.SetString("ddo_cogid", id);
		PlayerPrefs.Save();
	}

	public static string GetCogID()
	{
		return PlayerPrefs.GetString("ddo_cogid");
	}

	public static void SetApiToken(string token)
	{
		PlayerPrefs.SetString("ddo_api_token", token);
		PlayerPrefs.Save();
	}

	public static string GetApiToken()
	{
		return PlayerPrefs.GetString("ddo_api_token");
	}

	public static void SetReadTosVersion(int version)
	{
		PlayerPrefs.SetInt("ddo_read_tos_version", version);
		PlayerPrefs.Save();
	}

	public static int GetReadTosVersion()
	{
		return PlayerPrefs.GetInt("ddo_read_tos_version");
	}

	public static void SetCalendarMarkerFilter(CalendarMarkerFilterPackage filters)
	{
		string value = JsonUtility.ToJson(filters);
		PlayerPrefs.SetString("ddo_calendar_filter", value);
		PlayerPrefs.Save();
	}

	public static CalendarMarkerFilterPackage GetCalendarMarkerFilter()
	{
		string @string = PlayerPrefs.GetString("ddo_calendar_filter");
		return JsonUtility.FromJson<CalendarMarkerFilterPackage>(@string);
	}

	public static void SetCalendarBGImage(int index)
	{
		PlayerPrefs.SetInt("ddo_calendar_bg_image", index);
		PlayerPrefs.Save();
	}

	public static int GetCalendarBGImage()
	{
		return PlayerPrefs.GetInt("ddo_calendar_bg_image");
	}

	public static void SetCalendarReadTopic(CalendarUpdateInfoPackage package)
	{
		string value = JsonUtility.ToJson(package);
		PlayerPrefs.SetString("ddo_calendar_read_topic", value);
		PlayerPrefs.Save();
	}

	public static CalendarUpdateInfoPackage GetCalendarReadTopic()
	{
		string @string = PlayerPrefs.GetString("ddo_calendar_read_topic");
		return JsonUtility.FromJson<CalendarUpdateInfoPackage>(@string);
	}
}
