using UnityEngine;
using UnityEngine.UI;

public class TextSending : MonoBehaviour
{
	private Text Text;

	private TextAlphaSending TextAlphaSending;

	private void Start()
	{
		Text = GetComponent<Text>();
		TextAlphaSending = GetComponent<TextAlphaSending>();
		TextAlphaSending.Initialize();
	}

	private void Update()
	{
		if (!TextAlphaSending.IsEnd())
		{
			Text.SetAllDirty();
		}
	}
}
