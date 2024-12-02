using UnityEngine;
using UnityEngine.UI;

public class TabControl : MonoBehaviour
{
	[SerializeField]
	private Text titleText;

	public void OnValueChanged(bool isCheck)
	{
		if (isCheck)
		{
			titleText.text = GetComponentInChildren<Text>().text;
		}
	}
}
