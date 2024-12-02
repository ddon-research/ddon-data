using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class CalendarTopic
{
	[Serializable]
	public class TopicImageInfo
	{
		public string ImageUrl = string.Empty;

		public string LinkUrl = string.Empty;

		public bool IsOpen;
	}

	public enum ERROR_CODE
	{
		ERROR_CODE_SUCCESS,
		ERROR_CODE_DB_BREAK,
		ERROR_CODE_CMD_NOT_FOUND,
		ERROR_CODE_CAL_TYPE_INCORRECT,
		ERROR_CODE_DEFAULT_VALUE_NOT_FOUND,
		ERROR_CODE_CANNOT_GET_CLAN_INFO,
		ERROR_CODE_INTERNAL_ERROR,
		ERROR_CODE_TOPIC_NUM_OVER,
		ERROR_CODE_TOPIC_DELETED,
		ERROR_CODE_TOPIC_NOT_FOUND,
		ERROR_CODE_NOT_PERMISSION
	}

	public enum CALENDAR_TYPE
	{
		NONE,
		PRIVATE,
		CLAN,
		CLAN_MESSAGE_BOARD,
		EVENT,
		ALL
	}

	public ulong CalendarId;

	public ulong TopicId;

	public uint CharacterId;

	public CALENDAR_TYPE Type;

	public string BeginDate;

	public string EndDate;

	public string Title = string.Empty;

	public string Content = string.Empty;

	public uint LikeNum;

	public bool IsLiked;

	public string Created;

	public string ModifiedAt;

	public string UpdatedAt;

	public uint CommentNum;

	public string LikeUpdatedAt;

	public uint SlotNo;

	public List<TopicImageInfo> ImageInfoList = new List<TopicImageInfo>();

	public bool IsReported;

	public bool IsMaintainer;

	public const string BEGIN_NULL_DATE = "1900-01-01T00:00:00+09:00";

	public const string END_NULL_DATE = "2100-01-01T00:00:00+09:00";

	public static CALENDAR_TYPE CastCalendarType(int type)
	{
		if (Enum.IsDefined(typeof(CALENDAR_TYPE), (CALENDAR_TYPE)type))
		{
			return (CALENDAR_TYPE)type;
		}
		return CALENDAR_TYPE.NONE;
	}

	public bool IsIndefiniteBegin()
	{
		DateTime value = DateTime.Parse("1900-01-01T00:00:00+09:00");
		if (DateTime.Parse("1900-01-01T00:00:00+09:00").CompareTo(value) == 0)
		{
			return true;
		}
		return false;
	}

	public bool IsIndefiniteEnd()
	{
		DateTime value = DateTime.Parse("2100-01-01T00:00:00+09:00");
		if (DateTime.Parse("2100-01-01T00:00:00+09:00").CompareTo(value) == 0)
		{
			return true;
		}
		return false;
	}

	public static string DateTimeToString(DateTime date)
	{
		return date.ToString("yyyy-MM-ddTHH:mm:sszzz");
	}

	public static int CountChar(string s, char c)
	{
		int num = s.Length - s.Replace(c.ToString(), string.Empty).Length;
		return (num >= 0) ? num : 0;
	}
}
