using UnityEngine;
using UnityEngine.UI;

public class TutorialStartPage : MonoBehaviour
{
	public delegate void CallBack();

	[SerializeField]
	private Text InfoText;

	private CallBack m_OnLeft;

	private CallBack m_OnRight;

	public void OpenPage(CallBack left, CallBack right)
	{
		m_OnLeft = left;
		m_OnRight = right;
		base.gameObject.SetActive(value: true);
	}

	public void OpenPage(string text, CallBack left, CallBack right)
	{
		if (InfoText != null)
		{
			InfoText.text = text + "のチュートリアルを確認しますか?";
		}
		OpenPage(left, right);
	}

	public void ClosePage()
	{
		m_OnLeft = null;
		m_OnRight = null;
		base.gameObject.SetActive(value: false);
	}

	public void OnLeftButton()
	{
		if (m_OnLeft != null)
		{
			m_OnLeft();
		}
		ClosePage();
	}

	public void OnRightButton()
	{
		if (m_OnLeft != null)
		{
			m_OnRight();
		}
		ClosePage();
	}
}
