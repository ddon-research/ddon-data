using Packet;
using UnityEngine;

public class NewTopicIcon : MonoBehaviour
{
	[SerializeField]
	private GameObject Icon;

	private void Update()
	{
		if (SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance == null)
		{
			return;
		}
		uint num = SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.GetNewTopicNum(CalendarTopic.CALENDAR_TYPE.EVENT);
		if (SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.IsClanMember)
		{
			num += SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.GetNewTopicNum(CalendarTopic.CALENDAR_TYPE.CLAN);
			if (!SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.DidReadClanBoard())
			{
				num++;
			}
		}
		if (Icon.activeSelf != (num != 0))
		{
			Icon.SetActive(num != 0);
		}
	}
}
