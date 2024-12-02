using Packet;
using UnityEngine;
using UnityEngine.UI;

public class BazaarItemTableViewCell : TableViewCell<BazaarItem>
{
	[SerializeField]
	private new ItemIcon Icon;

	[SerializeField]
	private Text Name;

	[SerializeField]
	private Text ExhibitNum;

	[SerializeField]
	private BazaarItemSearchController Controller;

	private BazaarItem Data;

	private void Start()
	{
		GetComponent<Button>().onClick.AddListener(OnClick);
	}

	public override void UpdateContent(BazaarItem itemData)
	{
		Data = itemData;
		Icon.Load(itemData.Item.IconName, itemData.Item.IconColorId);
		Name.text = itemData.Item.Name;
		ExhibitNum.text = itemData.ExhibitNum.ToString();
	}

	public void OnClick()
	{
		Controller.OnClickElement(Data);
	}
}
