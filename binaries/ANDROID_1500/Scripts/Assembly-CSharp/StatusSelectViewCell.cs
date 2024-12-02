using UnityEngine;
using UnityEngine.UI;

public class StatusSelectViewCell : MonoBehaviour
{
	[SerializeField]
	private Text NameText;

	private uint CharacterId;

	private uint PawnId;

	private string Name = string.Empty;

	public void UpdateContent(uint characterId, uint pawnId, string name)
	{
		CharacterId = characterId;
		PawnId = pawnId;
		Name = name;
		NameText.text = name;
	}

	public void OnPushPlayer()
	{
		SingletonMonoBehaviour<ProfileManager>.Instance.OpenProfilePlayer(CharacterId);
	}

	public void OnPushMainPawn()
	{
		SingletonMonoBehaviour<ProfileManager>.Instance.OpenProfileMainPawn(SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData.CharacterID, PawnId);
	}

	public void OnPushSupportPawn()
	{
		SingletonMonoBehaviour<ProfileManager>.Instance.OpenProfileSupportPawn(PawnId);
	}
}
