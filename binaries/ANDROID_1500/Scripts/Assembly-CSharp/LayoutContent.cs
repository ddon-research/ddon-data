using UnityEngine;
using UnityEngine.UI;

public class LayoutContent : MonoBehaviour
{
	public enum Type
	{
		None,
		Vertical,
		Horizonal
	}

	private RectTransform m_RectTransform;

	private LayoutGroup m_LayOutGroup;

	private Type m_LayoutType;

	[SerializeField]
	private float m_Margin = 100f;

	private static float m_MarginSize = 2f;

	private void Start()
	{
		m_RectTransform = GetComponent<RectTransform>();
		m_LayOutGroup = GetComponent<LayoutGroup>();
		if (GetComponent<VerticalLayoutGroup>() != null)
		{
			m_LayoutType = Type.Vertical;
		}
		else if (GetComponent<HorizontalLayoutGroup>() != null)
		{
			m_LayoutType = Type.Horizonal;
		}
	}

	private void Update()
	{
		if (m_LayoutType == Type.Vertical)
		{
			if (Mathf.Abs(m_LayOutGroup.minHeight + m_Margin - m_RectTransform.sizeDelta.y) > m_MarginSize)
			{
				m_RectTransform.sizeDelta = new Vector2(m_RectTransform.sizeDelta.x, m_LayOutGroup.minHeight + m_Margin);
				m_RectTransform.anchoredPosition = new Vector2(0f, 0f);
			}
		}
		else if (Mathf.Abs(m_LayOutGroup.minWidth + m_Margin - m_RectTransform.sizeDelta.x) > m_MarginSize)
		{
			m_RectTransform.sizeDelta = new Vector2(m_LayOutGroup.minWidth + m_Margin, m_RectTransform.sizeDelta.y);
			m_RectTransform.anchoredPosition = new Vector2(0f, 0f);
		}
	}
}
