using System.Collections.Generic;
using UnityEngine;

public class SystemManager : SingletonMonoBehaviour<SystemManager>
{
	public enum PerformanceType
	{
		HIGH,
		LOW
	}

	private class PerformanceSetting
	{
		public int Fps;

		public PerformanceSetting(int fps)
		{
			Fps = fps;
		}
	}

	private string PerformanceKey = "ddo_performance_setting";

	private PerformanceType m_Performance;

	private Dictionary<PerformanceType, PerformanceSetting> m_PerformanceSetting = new Dictionary<PerformanceType, PerformanceSetting>();

	public PerformanceType Performance
	{
		get
		{
			return m_Performance;
		}
		set
		{
			m_Performance = value;
		}
	}

	private new void Awake()
	{
		base.Awake();
		QualitySettings.vSyncCount = 0;
		m_PerformanceSetting.Add(PerformanceType.HIGH, new PerformanceSetting(60));
		m_PerformanceSetting.Add(PerformanceType.LOW, new PerformanceSetting(30));
		LoadSetting();
	}

	public void LoadSetting()
	{
		m_Performance = (PerformanceType)PlayerPrefs.GetInt(PerformanceKey, 0);
		UpdateSetting();
	}

	public void SaveSetting()
	{
		PlayerPrefs.SetInt(PerformanceKey, (int)m_Performance);
		UpdateSetting();
	}

	private void UpdateSetting()
	{
		if (m_PerformanceSetting.ContainsKey(m_Performance))
		{
			PerformanceSetting performanceSetting = m_PerformanceSetting[m_Performance];
			Application.targetFrameRate = performanceSetting.Fps;
		}
	}
}
