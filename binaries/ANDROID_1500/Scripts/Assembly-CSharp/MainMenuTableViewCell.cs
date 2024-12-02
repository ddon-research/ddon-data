using UnityEngine;
using UnityEngine.UI;

public class MainMenuTableViewCell : TableViewCell<MainMenuData>
{
	[SerializeField]
	private GameObject HeaderObject;

	[SerializeField]
	private GameObject GroupObject;

	[SerializeField]
	private Text HeaderLabel;

	[SerializeField]
	private Text GroupLabel;

	public override void UpdateContent(MainMenuData itemData)
	{
		if (itemData.Type == MainMenuData.DataType.Header)
		{
			HeaderObject.SetActive(value: true);
			GroupObject.SetActive(value: false);
			HeaderLabel.text = itemData.Name;
		}
		else
		{
			HeaderObject.SetActive(value: false);
			GroupObject.SetActive(value: true);
			GroupLabel.text = itemData.Name;
		}
	}
}
