using System;
using System.Collections;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.EventSystems;
using WebRequest;

public class ServerUIController : SingletonMonoBehaviour<ServerUIController>
{
	[Serializable]
	public class UIElementSetting
	{
		public UIElementID ID;

		public GameObject Prefab;
	}

	[Serializable]
	public class UIIconSetting
	{
		public ServerUIIcon ID;

		public Sprite Icon;
	}

	[Serializable]
	public class UIBGSetting
	{
		public ServerUIBG ID;

		public Sprite BG;
	}

	[Serializable]
	public class UIWebBrowserSetting
	{
		public LinkType ID;

		public string URL;
	}

	[SerializeField]
	private UIElementSetting[] ElementSetting;

	private Dictionary<UIElementID, GameObject> Prefabs = new Dictionary<UIElementID, GameObject>();

	[SerializeField]
	private UIIconSetting[] IconSetting;

	private Dictionary<ServerUIIcon, Sprite> Icons = new Dictionary<ServerUIIcon, Sprite>();

	[SerializeField]
	private UIBGSetting[] BGSetting;

	private Dictionary<ServerUIBG, Sprite> BGs = new Dictionary<ServerUIBG, Sprite>();

	[SerializeField]
	private UIWebBrowserSetting[] WebBrowserSetting;

	private Dictionary<LinkType, string> WebBrowsers = new Dictionary<LinkType, string>();

	[SerializeField]
	private GameObject ServerUIPrefab;

	[SerializeField]
	private RectTransform ContentsFrame;

	[SerializeField]
	private RectTransform FullScreenFrame;

	private EventSystem EventSystem;

	private void Start()
	{
		UIElementSetting[] elementSetting = ElementSetting;
		foreach (UIElementSetting uIElementSetting in elementSetting)
		{
			if (uIElementSetting.ID != 0 && !Prefabs.ContainsKey(uIElementSetting.ID))
			{
				Prefabs.Add(uIElementSetting.ID, uIElementSetting.Prefab);
			}
		}
		UIIconSetting[] iconSetting = IconSetting;
		foreach (UIIconSetting uIIconSetting in iconSetting)
		{
			if (uIIconSetting.ID != 0 && !Icons.ContainsKey(uIIconSetting.ID))
			{
				Icons.Add(uIIconSetting.ID, uIIconSetting.Icon);
			}
		}
		UIBGSetting[] bGSetting = BGSetting;
		foreach (UIBGSetting uIBGSetting in bGSetting)
		{
			if (uIBGSetting.ID != 0 && !BGs.ContainsKey(uIBGSetting.ID))
			{
				BGs.Add(uIBGSetting.ID, uIBGSetting.BG);
			}
		}
		UIWebBrowserSetting[] webBrowserSetting = WebBrowserSetting;
		foreach (UIWebBrowserSetting uIWebBrowserSetting in webBrowserSetting)
		{
			if (uIWebBrowserSetting.ID > LinkType._WEB_BROWSER && !WebBrowsers.ContainsKey(uIWebBrowserSetting.ID))
			{
				WebBrowsers.Add(uIWebBrowserSetting.ID, uIWebBrowserSetting.URL);
			}
		}
		EventSystem = UnityEngine.Object.FindObjectOfType<EventSystem>();
	}

	public GameObject GetUIElement(UIElementID Id)
	{
		if (Prefabs.ContainsKey(Id))
		{
			return Prefabs[Id];
		}
		return null;
	}

	public Sprite GetIcon(ServerUIIcon Id)
	{
		if (Icons.ContainsKey(Id))
		{
			return Icons[Id];
		}
		return null;
	}

	public Sprite GetBG(ServerUIBG Id)
	{
		if (BGs.ContainsKey(Id))
		{
			return BGs[Id];
		}
		return null;
	}

	public string GetWebBrowserUrl(LinkType Id)
	{
		if (WebBrowsers.ContainsKey(Id))
		{
			return WebBrowsers[Id];
		}
		return string.Empty;
	}

	public void OpenServerUI(ServerUID UId, UIElementServerParam Param = null)
	{
		EventSystem.enabled = false;
		StartCoroutine(LoadRoutine(UId, (Param != null) ? Param : new UIElementServerParam()));
	}

	private IEnumerator LoadRoutine(ServerUID UId, UIElementServerParam Param)
	{
		yield return StartCoroutine(WebRequest.ServerUI.PostOpenServerUI(delegate(Packet.ServerUI res)
		{
			if (res.Error == ServerUIError.REQUEST_ERROR || res.Error == ServerUIError.INTERMAL_ERROR)
			{
				SingletonMonoBehaviour<ModalDialog>.Instance.Error(ModalDialog.Mode.OK, "リクエストエラー", res.Title);
			}
			else if (res.Error == ServerUIError.MESSAGE)
			{
				SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", res.Title);
			}
			else
			{
				GameObject gameObject = UnityEngine.Object.Instantiate(ServerUIPrefab);
				ServerUIBase component = gameObject.GetComponent<ServerUIBase>();
				RectTransform component2 = gameObject.GetComponent<RectTransform>();
				if (res.DispType == ServerUIDisp.FULL_SCREEN)
				{
					component2.SetParent(FullScreenFrame.transform, worldPositionStays: false);
					component.IsFullScreen = true;
				}
				else
				{
					component2.SetParent(ContentsFrame.transform, worldPositionStays: false);
				}
				component2.SetAsLastSibling();
				component.Setup(res);
				SingletonMonoBehaviour<NavigationViewController>.Instance.Push(component);
			}
		}, null, UId, Param, LoadingAnimation.Default));
	}
}
