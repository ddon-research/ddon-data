using System.Collections;
using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(Image))]
public class CharacterIconController : MonoBehaviour
{
	public enum SIZE
	{
		CHAR_ICON_L,
		CHAR_ICON_M,
		CHAR_ICON_S
	}

	private IEnumerator routine;

	private void OnEnable()
	{
		if (routine != null)
		{
			StartCoroutine(routine);
		}
	}

	public void LoadImageAsync(uint id, SIZE size = SIZE.CHAR_ICON_M)
	{
		if (id >= SingletonMonoBehaviour<ProfileManager>.Instance.CharacterIconMax)
		{
			Image component = GetComponent<Image>();
			if (component != null)
			{
				component.sprite = SingletonMonoBehaviour<ProfileManager>.Instance.DefaultCharacterIcon;
			}
			return;
		}
		string text = "size_m";
		string filePath = "Images/Character/" + text + "/char_" + id.ToString("00");
		routine = LoadManager.LoadAsync(filePath, delegate(Sprite res)
		{
			Image component2 = GetComponent<Image>();
			if (component2 != null)
			{
				component2.sprite = res;
			}
		});
		if (base.gameObject.activeInHierarchy)
		{
			StartCoroutine(routine);
		}
	}
}
