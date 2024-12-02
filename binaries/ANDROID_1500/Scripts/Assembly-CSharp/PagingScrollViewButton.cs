using UnityEngine;
using UnityEngine.UI;

public class PagingScrollViewButton : MonoBehaviour
{
	[SerializeField]
	private Image ImageEnabled;

	public void SetHightlightImageEnable(bool isEnable)
	{
		ImageEnabled.gameObject.SetActive(isEnable);
	}
}
