using System;

namespace Packet;

[Serializable]
public class UIElement
{
	public UIElementID Id;

	public UIElementType Type;

	public LinkType Link;

	public UIElementDispParam DispParam = new UIElementDispParam();

	public UIElementServerParam ServerParam = new UIElementServerParam();
}
