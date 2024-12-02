using System.Collections.Generic;
using Packet;
using UnityEngine;
using WebRequest;

public class TutorialManager : SingletonMonoBehaviour<TutorialManager>
{
	public enum TutorialType
	{
		NONE,
		TUTORIAL_MAIN,
		TUTORIAL_CALENDAR,
		TUTORIAL_ITEM_CREATE,
		TUTORIAL_BAZAAR_BUY,
		TUTORIAL_BAZAAR_SELL
	}

	public class TutorialData
	{
		public string Key;

		public string Title;

		public string PageUrl;

		public ushort PageMax;

		public bool Flag;

		public TutorialData(string key, string title, string pageUrl, ushort pageMax, bool flag)
		{
			Key = key;
			Title = title;
			PageUrl = pageUrl;
			PageMax = pageMax;
			Flag = flag;
		}
	}

	public TutorialController m_TutorialController;

	private Dictionary<TutorialType, TutorialData> m_TutorialData;

	public Dictionary<TutorialType, TutorialData> Tutorials => m_TutorialData;

	public bool IsLoading { get; private set; }

	private void Start()
	{
		m_TutorialData = new Dictionary<TutorialType, TutorialData>();
		m_TutorialData.Add(TutorialType.TUTORIAL_MAIN, new TutorialData("ddo_tutorial_main", "ホーム", string.Empty, 1, flag: false));
		m_TutorialData.Add(TutorialType.TUTORIAL_CALENDAR, new TutorialData("ddo_tutorial_calendar", "カレンダー", string.Empty, 1, flag: false));
		m_TutorialData.Add(TutorialType.TUTORIAL_ITEM_CREATE, new TutorialData("ddo_tutorial_item_create", "アイテム作成", string.Empty, 1, flag: false));
		m_TutorialData.Add(TutorialType.TUTORIAL_BAZAAR_BUY, new TutorialData("ddo_tutorial_bazaar_buy", "バザー購入", string.Empty, 1, flag: false));
		m_TutorialData.Add(TutorialType.TUTORIAL_BAZAAR_SELL, new TutorialData("ddo_tutorial_bazaar_sell", "バザー出品", string.Empty, 1, flag: false));
		IsLoading = true;
		NavigationViewController.AddProhibit(m_TutorialController.gameObject);
	}

	public void LoadTutorialData()
	{
		IsLoading = true;
		foreach (KeyValuePair<TutorialType, TutorialData> tutorialDatum in m_TutorialData)
		{
			tutorialDatum.Value.Flag = PlayerPrefs.GetInt(tutorialDatum.Value.Key, 0) != 0;
		}
		StartCoroutine(InGameURL.GetTutoriale(delegate(TutorialPathList res)
		{
			foreach (TutorialPath path in res.Paths)
			{
				if (m_TutorialData.ContainsKey((TutorialType)path.Id))
				{
					m_TutorialData[(TutorialType)path.Id].PageUrl = path.Path;
					m_TutorialData[(TutorialType)path.Id].PageMax = path.PageNum;
				}
				IsLoading = false;
			}
		}, null));
	}

	public bool isTutorialClear(TutorialType type)
	{
		if (m_TutorialData == null)
		{
			return false;
		}
		return m_TutorialData[type].Flag;
	}

	public void TutorialClear(TutorialType type)
	{
		if (m_TutorialData != null)
		{
			m_TutorialData[type].Flag = true;
			PlayerPrefs.SetInt(m_TutorialData[type].Key, 1);
			PlayerPrefs.Save();
		}
	}

	public void TutorialClearAll()
	{
		if (m_TutorialData == null)
		{
			return;
		}
		foreach (KeyValuePair<TutorialType, TutorialData> tutorialDatum in m_TutorialData)
		{
			m_TutorialData[tutorialDatum.Key].Flag = true;
			PlayerPrefs.SetInt(tutorialDatum.Value.Key, 1);
		}
		PlayerPrefs.Save();
	}

	public void TutorialResetAll()
	{
		if (m_TutorialData == null)
		{
			return;
		}
		foreach (KeyValuePair<TutorialType, TutorialData> tutorialDatum in m_TutorialData)
		{
			m_TutorialData[tutorialDatum.Key].Flag = false;
			PlayerPrefs.SetInt(tutorialDatum.Value.Key, 0);
		}
		PlayerPrefs.Save();
	}

	public void StartTutorial(TutorialType type, bool isMenu = false)
	{
		NavigationViewController.AddProhibit(m_TutorialController.gameObject);
		if (!isTutorialClear(type) || isMenu)
		{
			m_TutorialController.Setup(type, m_TutorialData[type].Title, ImageDownloader.CDNHost + m_TutorialData[type].PageUrl, m_TutorialData[type].PageMax, isMenu);
		}
	}
}
