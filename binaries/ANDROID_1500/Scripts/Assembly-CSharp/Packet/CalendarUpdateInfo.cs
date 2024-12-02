using System;

namespace Packet;

[Serializable]
public class CalendarUpdateInfo
{
	public enum ERROR_CODE
	{
		ERROR_CODE_SUCCESS,
		ERROR_CODE_CAL_TYPE_INCORRECT,
		ERROR_CODE_DEFAULT_VALUE_NOT_FOUND,
		ERROR_CODE_CANNOT_GET_CLAN_INFO
	}

	public ulong CalendarId;

	public ulong TopicId;

	public CalendarTopic.CALENDAR_TYPE Type;

	public string UpdateDate;

	public string BeginDate;

	public string EndDate;

	public string SelectDate = string.Empty;

	public DateTime GetUpdateTime()
	{
		return DateTime.Parse(UpdateDate);
	}

	public void SetDateTime(DateTime time)
	{
		UpdateDate = time.ToString("yyyy-MM-dd HH:mm:ss");
	}
}
