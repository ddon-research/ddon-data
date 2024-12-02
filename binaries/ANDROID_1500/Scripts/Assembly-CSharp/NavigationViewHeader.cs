using UnityEngine;
using UnityEngine.UI;

public class NavigationViewHeader : MonoBehaviour
{
	[SerializeField]
	private Image Icon;

	[SerializeField]
	private Text Title;

	public void UpdateContents(ViewController view)
	{
		if (view.Icon != null)
		{
			Icon.gameObject.SetActive(value: true);
			Icon.sprite = view.Icon;
		}
		if (!string.IsNullOrEmpty(view.Title))
		{
			Title.text = view.Title;
		}
	}
}
