using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(Text))]
public class ButtonText : MonoBehaviour
{
	[SerializeField]
	private Button m_Parent;

	private Text m_Text;

	private Color m_DefaultColor;

	private Color m_DisableColor;

	private bool m_IsEnable;

	private void Start()
	{
		m_Text = GetComponent<Text>();
		m_DefaultColor = m_Text.color;
		m_DisableColor = new Color(m_DefaultColor.r, m_DefaultColor.g, m_DefaultColor.b, 0.5f);
		m_IsEnable = true;
	}

	private void Update()
	{
		if (!(m_Parent == null) && m_Parent.interactable != m_IsEnable)
		{
			m_IsEnable = m_Parent.interactable;
			m_Text.color = ((!m_IsEnable) ? m_DisableColor : m_DefaultColor);
		}
	}
}
