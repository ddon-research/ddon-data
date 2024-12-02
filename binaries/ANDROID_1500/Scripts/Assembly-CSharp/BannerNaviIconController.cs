using UnityEngine;
using UnityEngine.UI;

public class BannerNaviIconController : ViewController
{
	[SerializeField]
	public Image EnableIconImage;

	public void SetEnable(bool b)
	{
		EnableIconImage.gameObject.SetActive(b);
	}
}
