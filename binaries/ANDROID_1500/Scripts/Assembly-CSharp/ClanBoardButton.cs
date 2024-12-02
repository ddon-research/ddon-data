using Packet;
using UnityEngine;
using UnityEngine.Networking;
using WebRequest;

public class ClanBoardButton : MonoBehaviour
{
	[SerializeField]
	private bool IsWaitingRequest;

	[SerializeField]
	private bool IsInit;

	[SerializeField]
	private ClanEmblem ProfileClanIcon;

	public void OnEnable()
	{
		if (!IsInit)
		{
			Init();
			IsInit = true;
		}
	}

	private void Init()
	{
		ProfileClanIcon.SetEmblemEmpry();
		StartCoroutine(CharacterData.GetCharacterProfile(delegate(PlayerProfile res)
		{
			if (res.ClanEmblem != null && res.Clan.ClanMember > 0)
			{
				ProfileClanIcon.SetEmblem(res.ClanEmblem.MarkType, res.ClanEmblem.BaseType, res.ClanEmblem.BaseMainColor, res.ClanEmblem.BaseSubColor);
			}
		}, delegate
		{
		}, SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData.CharacterID, CacheOption.OneMinute, LoadingAnimation.Default));
	}

	public void GetOpenClanBoard()
	{
		if (IsWaitingRequest)
		{
			return;
		}
		IsWaitingRequest = true;
		SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		StartCoroutine(CharacterCalendar.GetBoardTopic(delegate(CalendarTopicParam result)
		{
			IsWaitingRequest = false;
			if (result == null || result.TopicList.Count == 0)
			{
				SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "エラー", "クラン掲示板の取得に失敗しました。");
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			else
			{
				SingletonMonoBehaviour<ClanInfoCacheController>.Instance.UpdateClanMemberInfo(delegate
				{
					SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.UpdateUpdateInfo(delegate
					{
						SingletonMonoBehaviour<CalendarManager>.Instance.ClanTopicDetail.UpdateContent(result.TopicList[0]);
						SingletonMonoBehaviour<CalendarManager>.Instance.ClanTopicDetail.SelectDefaultTab();
						SingletonMonoBehaviour<NavigationViewController>.Instance.Push(SingletonMonoBehaviour<CalendarManager>.Instance.ClanTopicDetail);
						SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
					});
				});
			}
		}, delegate(UnityWebRequest result)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			IsWaitingRequest = false;
			AppUtility.ShowErr(result.downloadHandler.text, "CalendarTopic");
		}, CacheOption.Default));
	}
}
