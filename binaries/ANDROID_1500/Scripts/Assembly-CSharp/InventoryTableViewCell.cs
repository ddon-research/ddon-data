using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(Button))]
public class InventoryTableViewCell : TableViewCell<InventoryData>
{
	[SerializeField]
	private Text SlotNumText;

	[SerializeField]
	private Text ItemNameText;

	[SerializeField]
	private Text ItemNumLabelText;

	[SerializeField]
	private Text ItemNumText;

	[SerializeField]
	private Button Button;

	private Button ClickButton;

	public ulong ID { get; private set; }

	private void Start()
	{
		ClickButton = GetComponent<Button>();
		ClickButton.onClick.AddListener(OnClick);
	}

	public override void UpdateContent(InventoryData itemData)
	{
		SlotNumText.text = itemData.SlotNo.ToString();
		if (!itemData.IsEmpty)
		{
			ItemNameText.text = itemData.ItemName;
			ItemNumText.text = itemData.ItemNum.ToString();
			ItemNumLabelText.gameObject.SetActive(value: true);
			Button.interactable = true;
		}
		else
		{
			ItemNameText.text = string.Empty;
			ItemNumText.text = string.Empty;
			ItemNumLabelText.gameObject.SetActive(value: false);
			Button.interactable = false;
		}
	}

	public void OnClick()
	{
	}
}
