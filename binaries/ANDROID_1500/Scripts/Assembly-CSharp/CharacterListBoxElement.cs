using Packet;
using UnityEngine;
using UnityEngine.UI;

public class CharacterListBoxElement : ListBoxElement<LoginCharacterList.ListElement>
{
	[SerializeField]
	public Text FirstNameLabel;

	[SerializeField]
	public Text LastNameLabel;

	[SerializeField]
	public CharacterIconController CharacterIcon;

	[SerializeField]
	public uint CharacterID { get; private set; }

	public override void UpdateContent(LoginCharacterList.ListElement data)
	{
		CharacterID = data.CharacterID;
		FirstNameLabel.text = data.FirstName;
		LastNameLabel.text = data.LastName;
		CharacterIcon.LoadImageAsync(data.IconID);
	}
}
