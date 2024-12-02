using Packet;
using UnityEngine;
using UnityEngine.UI;

public class ServerUIBase : ViewController
{
	[SerializeField]
	private ScrollRect ScrollVeiw;

	[SerializeField]
	private Image BG;

	public void Setup(ServerUI Param)
	{
		BaseTitle = Param.Title;
		BaseIcon = SingletonMonoBehaviour<ServerUIController>.Instance.GetIcon(Param.IconId);
		if (Param.BG != 0)
		{
			BG.sprite = SingletonMonoBehaviour<ServerUIController>.Instance.GetBG(Param.BG);
		}
		else
		{
			BG.enabled = false;
		}
		foreach (UIElement uIElement2 in Param.UIElements)
		{
			GameObject gameObject = null;
			GameObject uIElement = SingletonMonoBehaviour<ServerUIController>.Instance.GetUIElement(uIElement2.Id);
			if (uIElement != null)
			{
				gameObject = Object.Instantiate(uIElement);
			}
			if (!(gameObject == null))
			{
				ServerUIElementBase component = gameObject.GetComponent<ServerUIElementBase>();
				RectTransform component2 = gameObject.GetComponent<RectTransform>();
				if (uIElement2.Type == UIElementType.FOOTER)
				{
					component2.SetParent(Option.CachedRectTransform, worldPositionStays: false);
				}
				else
				{
					component2.SetParent(ScrollVeiw.content, worldPositionStays: false);
				}
				component2.SetAsLastSibling();
				component.Setup(uIElement2);
			}
		}
	}
}
