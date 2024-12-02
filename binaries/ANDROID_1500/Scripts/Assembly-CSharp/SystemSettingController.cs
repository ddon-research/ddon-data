using UnityEngine;
using UnityEngine.UI;

public class SystemSettingController : ViewController
{
	[SerializeField]
	private Slider m_PerformanceSlider;

	private void Initialize()
	{
		m_PerformanceSlider.value = (float)SingletonMonoBehaviour<SystemManager>.Instance.Performance;
	}

	private void OnEnable()
	{
		Initialize();
	}

	public void OnPerformanceChanged()
	{
		SystemManager.PerformanceType performanceType = (SystemManager.PerformanceType)m_PerformanceSlider.value;
		if (performanceType != SingletonMonoBehaviour<SystemManager>.Instance.Performance)
		{
			SingletonMonoBehaviour<SystemManager>.Instance.Performance = performanceType;
			SingletonMonoBehaviour<SystemManager>.Instance.SaveSetting();
		}
	}
}
