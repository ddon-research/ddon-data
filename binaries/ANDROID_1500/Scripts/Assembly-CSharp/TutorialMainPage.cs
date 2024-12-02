using System.Collections.Generic;
using UnityEngine;

public class TutorialMainPage : MonoBehaviour
{
	public delegate void CallBack();

	[SerializeField]
	private PageScrollVeiw Veiw;

	[SerializeField]
	private TutorialPage Page;

	private CallBack m_OnClose;

	private List<Texture2D> m_TextureList;

	private List<TutorialPage> m_PageList = new List<TutorialPage>();

	private void Update()
	{
		for (int i = 0; i < m_TextureList.Count; i++)
		{
			if (m_PageList[i].texture != m_TextureList[i])
			{
				m_PageList[i].texture = m_TextureList[i];
			}
		}
	}

	public void OpenPage(List<Texture2D> list, CallBack close)
	{
		m_TextureList = list;
		m_OnClose = close;
		m_TextureList = list;
		for (int i = 0; i < m_TextureList.Count; i++)
		{
			if (m_PageList.Count <= i)
			{
				TutorialPage tutorialPage = Object.Instantiate(Page);
				tutorialPage.GetComponent<RectTransform>().SetParent(Page.transform.parent, worldPositionStays: false);
				tutorialPage.gameObject.SetActive(value: true);
				tutorialPage.GetComponent<RectTransform>().SetAsLastSibling();
				tutorialPage.texture = null;
				m_PageList.Add(tutorialPage);
			}
			else
			{
				m_PageList[i].gameObject.SetActive(value: true);
				m_PageList[i].texture = null;
			}
		}
		for (int j = m_TextureList.Count; j < m_PageList.Count; j++)
		{
			m_PageList[j].gameObject.SetActive(value: false);
		}
		Veiw.SetupPage();
		base.gameObject.SetActive(value: true);
	}

	public void ClosePage()
	{
		base.gameObject.SetActive(value: false);
	}

	public void OnCloseButton()
	{
		if (m_OnClose != null)
		{
			m_OnClose();
		}
		ClosePage();
	}
}
