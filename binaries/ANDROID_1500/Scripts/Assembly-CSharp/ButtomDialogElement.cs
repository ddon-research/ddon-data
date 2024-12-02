using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(Button))]
public class ButtomDialogElement : ViewController
{
	[SerializeField]
	private Text ButtonText;

	public void UpdateContent(ButtomDialogController parent, ButtomDialogData data)
	{
		ButtonText.text = data.Name;
		Button component = GetComponent<Button>();
		if (!(component == null))
		{
			component.onClick.AddListener(data.OnClick);
		}
	}
}
