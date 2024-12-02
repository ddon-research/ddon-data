using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(Toggle))]
public class ToggleImageGroup : MonoBehaviour
{
	private Toggle m_Toggle;

	private bool m_isToggleOn;

	[SerializeField]
	private Image[] Images;

	[SerializeField]
	private Text[] Texts;

	[SerializeField]
	private Color[] FontColor = new Color[2];

	private void Start()
	{
		m_Toggle = GetComponent<Toggle>();
		UpdateToggle();
	}

	private void Update()
	{
		if (m_Toggle.isOn != m_isToggleOn)
		{
			UpdateToggle();
		}
	}

	private void UpdateToggle()
	{
		m_isToggleOn = m_Toggle.isOn;
		if (Images != null)
		{
			Image[] images = Images;
			foreach (Image image in images)
			{
				image.enabled = m_isToggleOn;
			}
		}
		if (Texts != null && FontColor != null)
		{
			Text[] texts = Texts;
			foreach (Text text in texts)
			{
				text.color = FontColor[m_isToggleOn ? 1 : 0];
			}
		}
	}
}
