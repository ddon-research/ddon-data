using Packet;
using UnityEngine;

public class NewTopicsController : MonoBehaviour
{
	[SerializeField]
	private NewTopics PrivateTopics;

	[SerializeField]
	private NewTopics ClanTopics;

	[SerializeField]
	private NewTopics OfficialTopics;

	[SerializeField]
	private NewClanBoardTopics ClanBoard;

	private bool IsInit;

	public void OnEnable()
	{
		if (!IsInit)
		{
			SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.MarkReload();
			IsInit = true;
		}
		SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.UpdateUpdateInfo(delegate
		{
			uint privateTopicNum = SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.PrivateTopicNum;
			uint privateTopicMax = SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.PrivateTopicMax;
			uint clanTopicNum = SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.ClanTopicNum;
			uint clanTopicMax = SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.ClanTopicMax;
			uint officialTopicNum = SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.OfficialTopicNum;
			uint officialTopicMax = SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.OfficialTopicMax;
			uint newNum = 0u;
			PrivateTopics.UpdateContent(privateTopicNum, privateTopicMax, newNum);
			uint newTopicNum = SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.GetNewTopicNum(CalendarTopic.CALENDAR_TYPE.CLAN);
			bool isNew = !SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.DidReadClanBoard();
			if (SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.IsClanMember)
			{
				ClanTopics.UpdateContent(clanTopicNum, clanTopicMax, newTopicNum);
				ClanBoard.UpdateContent(isNew);
			}
			else
			{
				ClanTopics.UpdateContent(clanTopicNum, clanTopicMax, 0u);
				ClanBoard.UpdateContent(IsNew: false);
			}
			uint newTopicNum2 = SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.GetNewTopicNum(CalendarTopic.CALENDAR_TYPE.EVENT);
			OfficialTopics.UpdateContent(officialTopicNum, officialTopicMax, newTopicNum2, isDisplayMax: false);
		});
	}
}
