using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class TopicComment
{
	public enum ERROR_CODE
	{
		ERROR_CODE_SUCCESS,
		ERROR_CODE_DB_BREAK,
		ERROR_CODE_CMD_NOT_FOUND,
		ERROR_CODE_CAL_TYPE_INCORRECT,
		ERROR_CODE_CANNOT_GET_CALENDAR,
		ERROR_CODE_CANNOT_GET_CLAN_INFO,
		ERROR_CODE_DEFAULT_VALUE_NOT_FOUND,
		ERROR_CODE_INVALID_DATA,
		ERROR_CODE_COMMENT_NUM_OVER
	}

	public ulong CommentId;

	public ulong CalendarId;

	public ulong TopicId;

	public uint No;

	public uint CharacterId;

	public string Content;

	public string Created;

	public string UpdatedAt;

	public uint LikeNum;

	public bool IsLiked;

	public bool IsReported;

	public List<CalendarTopic.TopicImageInfo> ImageInfoList = new List<CalendarTopic.TopicImageInfo>();

	public TopicComment Clone()
	{
		return (TopicComment)MemberwiseClone();
	}
}
