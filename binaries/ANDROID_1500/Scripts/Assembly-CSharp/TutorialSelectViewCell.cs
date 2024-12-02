using UnityEngine;
using UnityEngine.UI;

public class TutorialSelectViewCell : MonoBehaviour
{
	[SerializeField]
	private Text Text;

	private TutorialManager.TutorialType m_Type;

	private TutorialManager.TutorialData m_Data;

	public void Setup(TutorialManager.TutorialType type, TutorialManager.TutorialData data)
	{
		m_Type = type;
		m_Data = data;
		Text.text = m_Data.Title;
	}

	public void OnPush()
	{
		SingletonMonoBehaviour<TutorialManager>.Instance.StartTutorial(m_Type, isMenu: true);
	}
}
