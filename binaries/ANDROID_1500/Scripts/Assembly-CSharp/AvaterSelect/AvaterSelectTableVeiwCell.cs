using UnityEngine;
using UnityEngine.UI;

namespace AvaterSelect;

public class AvaterSelectTableVeiwCell : TableViewCell<Data>
{
	[SerializeField]
	private AvaterSelectController controller;

	[SerializeField]
	private Image[] IconImage;

	[SerializeField]
	private Image[] SelectedImage;

	private uint RowIndex;

	private void Update()
	{
		for (uint num = 0u; num < 4; num++)
		{
			if (controller.SelectedRow == RowIndex && controller.SelectedColumn == num)
			{
				SelectedImage[num].gameObject.SetActive(value: true);
			}
			else
			{
				SelectedImage[num].gameObject.SetActive(value: false);
			}
		}
	}

	public override void UpdateContent(Data itemData)
	{
		RowIndex = itemData.RowIndex;
		for (uint num = 0u; num < 4; num++)
		{
			if (SingletonMonoBehaviour<ProfileManager>.Instance.CharacterIconMax <= itemData.IconIDs[num])
			{
				IconImage[num].transform.parent.gameObject.SetActive(value: false);
				continue;
			}
			IconImage[num].transform.parent.gameObject.SetActive(value: true);
			string filePath = $"Images/Character/size_m/char_{itemData.IconIDs[num]:00}";
			StartCoroutine(LoadManager.LoadAsync(filePath, delegate(Sprite res, uint index)
			{
				Image image = IconImage[index];
				if (image != null)
				{
					image.sprite = res;
				}
			}, num));
		}
	}

	public void OnClickAvator(int column)
	{
		controller.SelectAvater(RowIndex, (uint)column);
	}
}
