using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(Button))]
public class Mail_ListTableVewCell : TableViewCell<MailListData>
{
	private Button ClickButton;

	[SerializeField]
	private Text SenderFirstName;

	[SerializeField]
	private Text SenderLastName;

	[SerializeField]
	private Text ReceivedAt;

	[SerializeField]
	private Text TitleLabel;

	[SerializeField]
	private Image OpenIcon;

	[SerializeField]
	private Image CloseIcon;

	[SerializeField]
	private CharacterIconController CharacterIcon;

	[SerializeField]
	private Mail_Detail MailDatailPage;

	public ulong ID { get; private set; }

	private void Start()
	{
		ClickButton = GetComponent<Button>();
		ClickButton.onClick.AddListener(OnClick);
	}

	public override void UpdateContent(MailListData itemData)
	{
		SenderFirstName.text = itemData.SenderFirstName;
		SenderLastName.text = itemData.SenderLastName;
		TitleLabel.text = itemData.Title;
		ReceivedAt.text = itemData.ReceivedAt.ToString("yyyy/MM/dd (ddd) HH:mm");
		if (itemData.Status == MailListData.ReadStatus.Read)
		{
			OpenIcon.gameObject.SetActive(value: true);
			CloseIcon.gameObject.SetActive(value: false);
		}
		else
		{
			OpenIcon.gameObject.SetActive(value: false);
			CloseIcon.gameObject.SetActive(value: true);
		}
		CharacterIcon.LoadImageAsync(itemData.CharacterIconID);
		ID = itemData.ID;
	}

	public void OnClick()
	{
		MailDatailPage.ID = ID;
		SingletonMonoBehaviour<NavigationViewController>.Instance.Push(MailDatailPage);
	}
}
