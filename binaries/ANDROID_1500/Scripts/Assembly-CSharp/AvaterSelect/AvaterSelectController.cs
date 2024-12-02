using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

namespace AvaterSelect;

public class AvaterSelectController : ViewController
{
	[SerializeField]
	private Image SelectedAvaterImage;

	[SerializeField]
	private Text FirstNameText;

	[SerializeField]
	private Text LastNameText;

	public uint SelectedRow { get; private set; }

	public uint SelectedColumn { get; private set; }

	private void OnEnable()
	{
		CharacterDataBase characterData = SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData;
		CalcRowColumnFromIconID(characterData.IconID, out var row, out var column);
		SelectAvater(row, column);
		FirstNameText.text = characterData.FirstName;
		LastNameText.text = characterData.LastName;
	}

	private uint GetSelectedIconID()
	{
		return SelectedRow * 4 + SelectedColumn;
	}

	public void SelectAvater(uint row, uint column)
	{
		SelectedRow = row;
		SelectedColumn = column;
		uint num = row * 4 + column;
		if (num >= SingletonMonoBehaviour<ProfileManager>.Instance.CharacterIconMax)
		{
			if (SelectedAvaterImage != null)
			{
				SelectedAvaterImage.sprite = SingletonMonoBehaviour<ProfileManager>.Instance.DefaultCharacterIcon;
			}
			return;
		}
		string filePath = $"Images/Character/size_m/char_{num:00}";
		StartCoroutine(LoadManager.LoadAsync(filePath, delegate(Sprite res)
		{
			if (SelectedAvaterImage != null)
			{
				SelectedAvaterImage.sprite = res;
			}
		}));
	}

	public void OnDicide()
	{
		StartCoroutine(CharacterData.PutIcon(delegate
		{
			SingletonMonoBehaviour<NavigationViewController>.Instance.Pop();
			MainViewController.Instance.UpdateIcon(GetSelectedIconID());
		}, null, GetSelectedIconID(), LoadingAnimation.Default));
	}

	public void OnCancel()
	{
		SingletonMonoBehaviour<NavigationViewController>.Instance.Pop();
	}

	public static void CalcRowColumnFromIconID(uint id, out uint row, out uint column)
	{
		row = id / 4;
		column = id % 4;
	}
}
