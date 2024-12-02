using UnityEngine;
using UnityEngine.UI;

public class TutorialPage : MonoBehaviour
{
	[SerializeField]
	private GameObject LoadIcon;

	[SerializeField]
	private RawImage Image;

	public Texture texture
	{
		get
		{
			if (Image == null)
			{
				return null;
			}
			return Image.texture;
		}
		set
		{
			if (!(Image == null))
			{
				SetPage(value);
			}
		}
	}

	private void SetPage(Texture tex)
	{
		if (tex == null)
		{
			Image.color = Color.black;
			LoadIcon.SetActive(value: true);
		}
		else
		{
			Image.color = Color.white;
			Image.texture = tex;
			LoadIcon.SetActive(value: false);
		}
	}
}
