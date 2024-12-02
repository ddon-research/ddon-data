using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class ServerUI
{
	public ServerUID Id;

	public ServerUIIcon IconId;

	public ServerUIBG BG;

	public ServerUIDisp DispType;

	public string Title;

	public List<UIElement> UIElements = new List<UIElement>();

	public ServerUIError Error;
}
