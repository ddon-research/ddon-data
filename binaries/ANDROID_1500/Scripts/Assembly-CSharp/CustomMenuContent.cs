using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(Button))]
public class CustomMenuContent : MonoBehaviour
{
	[SerializeField]
	private Text ButtonText;

	public void UpdateContent(ICustomMenu parent, CustomMenuContentData data)
	{
		ButtonText.text = data.Name;
		ButtonText.color = data.TextColor;
		Button component = GetComponent<Button>();
		if (component == null)
		{
			return;
		}
		component.onClick.AddListener(delegate
		{
			if (!parent.IsChanging)
			{
				parent.Deactivate();
				if (data.OnClick != null)
				{
					data.OnClick();
				}
			}
		});
	}
}
