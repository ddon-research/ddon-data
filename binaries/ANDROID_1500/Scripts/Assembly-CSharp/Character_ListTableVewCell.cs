using Packet;
using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(Button))]
public class Character_ListTableVewCell : TableViewCell<LoginCharacterList.ListElement>
{
	private Button ClickButton;

	[SerializeField]
	private Text TitleLabel;

	public uint ID { get; private set; }

	private void Start()
	{
		ClickButton = GetComponent<Button>();
		ClickButton.onClick.AddListener(OnClick);
	}

	public override void UpdateContent(LoginCharacterList.ListElement characterData)
	{
		TitleLabel.text = characterData.FirstName + " " + characterData.LastName;
	}

	public void OnClick()
	{
	}
}
