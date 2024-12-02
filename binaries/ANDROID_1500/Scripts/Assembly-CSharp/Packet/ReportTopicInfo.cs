using System;

namespace Packet;

[Serializable]
public class ReportTopicInfo : Report
{
	public ulong TopicId;

	public ulong CommentId;

	public string ReportText;

	public ReportTopicInfo(uint charId, ulong tid, ulong cmid, string txt)
	{
		ReportedCharId = charId;
		TopicId = tid;
		CommentId = cmid;
		ReportText = txt;
	}
}
