using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class PageControl : MonoBehaviour
{
	[SerializeField]
	private Toggle IndicatorBase;

	private List<Toggle> Indicators = new List<Toggle>();

	private void Awake()
	{
		if (IndicatorBase != null)
		{
			IndicatorBase.gameObject.SetActive(value: false);
		}
	}

	public void SetNumberOfPages(int number)
	{
		if (Indicators.Count < number)
		{
			for (int i = Indicators.Count; i < number; i++)
			{
				Toggle toggle = Object.Instantiate(IndicatorBase);
				toggle.gameObject.SetActive(value: true);
				toggle.transform.SetParent(IndicatorBase.transform.parent);
				toggle.transform.localScale = IndicatorBase.transform.localScale;
				toggle.isOn = false;
				Indicators.Add(toggle);
			}
		}
		else if (Indicators.Count > number)
		{
			for (int num = Indicators.Count - 1; num >= number; num--)
			{
				Object.Destroy(Indicators[num].gameObject);
				Indicators.RemoveAt(num);
			}
		}
	}

	public void AddPage(string name)
	{
		Toggle toggle = Object.Instantiate(IndicatorBase);
		toggle.gameObject.SetActive(value: true);
		toggle.transform.SetParent(IndicatorBase.transform.parent);
		toggle.transform.localScale = IndicatorBase.transform.localScale;
		toggle.transform.GetComponentInChildren<Text>().text = name;
		toggle.isOn = false;
		Indicators.Add(toggle);
	}

	public void SetCurrentPage(int index)
	{
		if (index >= 0 && index < Indicators.Count)
		{
			Indicators[index].isOn = true;
		}
	}
}
