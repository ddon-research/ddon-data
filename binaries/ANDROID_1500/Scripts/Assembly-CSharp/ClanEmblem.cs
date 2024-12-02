using UnityEngine;
using UnityEngine.UI;

public class ClanEmblem : MonoBehaviour
{
	[SerializeField]
	private Image EmptyImage;

	[SerializeField]
	private Image EmblemImage;

	[SerializeField]
	private Image BaseImage;

	[SerializeField]
	private Image MarkImage;

	public void SetEmblemEmpry()
	{
		EmptyImage.gameObject.SetActive(value: true);
		EmblemImage.gameObject.SetActive(value: false);
	}

	public void SetEmblem(ushort markType, ushort baseType, ushort mainColor, ushort subColor)
	{
		EmblemImage.color = SingletonMonoBehaviour<ProfileManager>.Instance.GetClanEmblemColor(subColor);
		BaseImage.sprite = SingletonMonoBehaviour<ProfileManager>.Instance.GetClanBase(baseType);
		BaseImage.color = SingletonMonoBehaviour<ProfileManager>.Instance.GetClanEmblemColor(mainColor);
		MarkImage.sprite = SingletonMonoBehaviour<ProfileManager>.Instance.GetClanMark(markType);
		EmptyImage.gameObject.SetActive(value: false);
		EmblemImage.gameObject.SetActive(value: true);
	}
}
