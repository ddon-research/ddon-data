using UnityEngine;
using UnityEngine.UI;

public class SendMemberListElement : MonoBehaviour
{
	[SerializeField]
	private CharacterIconController CharacterIcon;

	[SerializeField]
	private Text FirstName;

	[SerializeField]
	private Text Lastname;

	public void UpdateContents(uint iconId, string firstName, string lastName)
	{
		CharacterIcon.LoadImageAsync(iconId);
		FirstName.text = firstName;
		Lastname.text = lastName;
	}
}
