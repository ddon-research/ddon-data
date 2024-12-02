using Packet;
using UnityEngine;

public class DayListViewController : ViewController
{
	[SerializeField]
	private DayListController _MyController;

	public DayListController MyController
	{
		get
		{
			return _MyController;
		}
		private set
		{
			_MyController = value;
		}
	}

	public override void OnNavigationPushEnd()
	{
		MyController.OnNavigationPushEnd();
	}

	public override void OnNavigationPopBegin()
	{
		MyController.OnNavigationPopBegin();
	}

	public void OpenCreateTopic()
	{
		if (SingletonMonoBehaviour<LoadController>.Instance.IsActive)
		{
			return;
		}
		SingletonMonoBehaviour<ClanInfoCacheController>.Instance.UpdateClanMemberInfo(delegate
		{
			uint characterID = SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData.CharacterID;
			ClanMemberListElement characterInfo = SingletonMonoBehaviour<ClanInfoCacheController>.Instance.GetCharacterInfo(characterID);
			if (characterInfo != null && (characterInfo.MemberRank == 1 || characterInfo.MemberRank == 2))
			{
				SingletonMonoBehaviour<CalendarManager>.Instance.CreateTopic.ResetPage(CalendarTopic.CALENDAR_TYPE.NONE, CreateTopic.CREATE_FLOW_TYPE.DAY_LIST, MyController.SelectDate);
			}
			else
			{
				SingletonMonoBehaviour<CalendarManager>.Instance.CreateTopic.ResetPage(CalendarTopic.CALENDAR_TYPE.PRIVATE, CreateTopic.CREATE_FLOW_TYPE.DAY_LIST, MyController.SelectDate);
			}
			if (!SingletonMonoBehaviour<LoadController>.Instance.IsActive)
			{
				SingletonMonoBehaviour<NavigationViewController>.Instance.Push(SingletonMonoBehaviour<CalendarManager>.Instance.CreateTopic);
			}
		});
	}
}
