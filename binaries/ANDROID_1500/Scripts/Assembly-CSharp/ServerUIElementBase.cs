using Packet;
using UnityEngine;

public abstract class ServerUIElementBase : MonoBehaviour
{
	protected LinkType Link;

	protected UIElementDispParam DispParam;

	protected UIElementServerParam ServerParam;

	public void Setup(UIElement Param)
	{
		Link = Param.Link;
		DispParam = Param.DispParam;
		ServerParam = Param.ServerParam;
		SetupElement();
	}

	public abstract void SetupElement();

	public virtual void OnPush()
	{
		if (Link == LinkType.INVALID)
		{
			return;
		}
		if (Link > LinkType._WEB_BROWSER)
		{
			string empty = string.Empty;
			empty = ((Link != LinkType.WEB_BROWSER_TEXT1) ? SingletonMonoBehaviour<ServerUIController>.Instance.GetWebBrowserUrl(Link) : ServerParam.Text1);
			if (empty != string.Empty)
			{
				Application.OpenURL(empty);
			}
		}
		else if (Link <= LinkType._CLIENT_UI)
		{
			SingletonMonoBehaviour<ServerUIController>.Instance.OpenServerUI((ServerUID)Link, ServerParam);
		}
	}
}
