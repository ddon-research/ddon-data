using System;

namespace Packet;

[Serializable]
public class CalendarAbstract
{
	public enum ERROR_CODE
	{
		ERROR_CODE_SUCCESS,
		ERROR_CODE_DB_BREAK,
		ERROR_CODE_CMD_NOT_FOUND,
		ERROR_CODE_CAL_TYPE_INCORRECT
	}

	public ulong CalendarId;

	public ulong TopicId;

	public CalendarTopic.CALENDAR_TYPE Type;

	public string BeginDate;

	public string EndDate;
}
