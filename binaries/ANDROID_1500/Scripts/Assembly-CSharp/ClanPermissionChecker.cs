using Packet;
using UnityEngine;

public class ClanPermissionChecker : MonoBehaviour
{
	[SerializeField]
	private GameObject Target;

	public void OnEnable()
	{
		SingletonMonoBehaviour<ClanInfoCacheController>.Instance.UpdateClanMemberInfo(delegate
		{
			uint characterID = SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData.CharacterID;
			ClanMemberListElement characterInfo = SingletonMonoBehaviour<ClanInfoCacheController>.Instance.GetCharacterInfo(characterID);
			if (characterInfo == null)
			{
				Target.SetActive(value: false);
			}
			else if (characterInfo.MemberRank == 1 || characterInfo.MemberRank == 2)
			{
				Target.SetActive(value: true);
			}
			else
			{
				Target.SetActive(value: false);
			}
		});
	}
}
