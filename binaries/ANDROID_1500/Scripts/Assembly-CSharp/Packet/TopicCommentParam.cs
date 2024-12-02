using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class TopicCommentParam
{
	public uint TotalNum;

	public uint PageSize;

	public uint MaxLimit;

	public uint ActualTotalNum;

	public string TopicUpdatedAt;

	public List<TopicComment> CommentList = new List<TopicComment>();
}
