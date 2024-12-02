using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TutorialController : MonoBehaviour
{
	[SerializeField]
	private TutorialStartPage SetupPage;

	[SerializeField]
	public TutorialStartPage StartPage;

	[SerializeField]
	private TutorialMainPage MainPage;

	private TutorialManager.TutorialType m_Type;

	private string m_Url;

	private ushort m_PageMax;

	private List<Texture2D> m_TextureList = new List<Texture2D>();

	public void Setup(TutorialManager.TutorialType type, string title, string url, ushort pageMax, bool isMenu = false)
	{
		m_Type = type;
		m_Url = url;
		m_PageMax = pageMax;
		SetupPage.gameObject.SetActive(value: false);
		StartPage.gameObject.SetActive(value: false);
		MainPage.gameObject.SetActive(value: false);
		base.gameObject.SetActive(value: true);
		if (isMenu)
		{
			LoadImage();
			MainPage.OpenPage(m_TextureList, delegate
			{
				End();
			});
			return;
		}
		if (type == TutorialManager.TutorialType.TUTORIAL_MAIN)
		{
			SetupPage.OpenPage(delegate
			{
				LoadImage();
				MainPage.OpenPage(m_TextureList, delegate
				{
					SingletonMonoBehaviour<TutorialManager>.Instance.TutorialClear(m_Type);
					End();
				});
			}, delegate
			{
				SingletonMonoBehaviour<TutorialManager>.Instance.TutorialClearAll();
				End();
			});
			return;
		}
		StartPage.OpenPage(title, delegate
		{
			LoadImage();
			MainPage.OpenPage(m_TextureList, delegate
			{
				SingletonMonoBehaviour<TutorialManager>.Instance.TutorialClear(m_Type);
				End();
			});
		}, delegate
		{
			SingletonMonoBehaviour<TutorialManager>.Instance.TutorialClear(m_Type);
			End();
		});
	}

	public void End()
	{
		for (ushort num = 0; num < m_TextureList.Count; num++)
		{
			if (m_TextureList[num] != null)
			{
				Object.Destroy(m_TextureList[num]);
			}
		}
		m_TextureList.Clear();
		base.gameObject.SetActive(value: false);
	}

	private void LoadImage()
	{
		for (ushort num = 0; num < m_TextureList.Count; num++)
		{
			if (m_TextureList[num] != null)
			{
				Object.Destroy(m_TextureList[num]);
			}
		}
		m_TextureList.Clear();
		for (ushort num2 = 0; num2 < m_PageMax; num2++)
		{
			m_TextureList.Add(null);
		}
		StartCoroutine(LoadImageRoutine(m_Url, m_PageMax, m_TextureList));
	}

	private IEnumerator LoadImageRoutine(string url, ushort pageNum, List<Texture2D> list)
	{
		ushort request = 0;
		for (short i = 0; i < (short)pageNum; i++)
		{
			WWW www = new WWW(url + i.ToString("D2") + ".png");
			yield return www;
			if (www.error == null)
			{
				list[i] = www.textureNonReadable;
				request = 0;
			}
			else
			{
				list[i] = null;
				request++;
				if (request < 3)
				{
					i--;
				}
				else
				{
					request = 0;
				}
			}
		}
		yield return null;
	}
}
