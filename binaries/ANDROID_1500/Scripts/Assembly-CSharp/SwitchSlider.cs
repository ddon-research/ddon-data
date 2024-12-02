using UnityEngine;
using UnityEngine.UI;

public class SwitchSlider : MonoBehaviour
{
	private Slider m_Slider;

	private void Start()
	{
		m_Slider = GetComponent<Slider>();
	}

	public void Switch()
	{
		if (m_Slider.value > 0f)
		{
			m_Slider.value = 0f;
		}
		else
		{
			m_Slider.value = 1f;
		}
	}
}
