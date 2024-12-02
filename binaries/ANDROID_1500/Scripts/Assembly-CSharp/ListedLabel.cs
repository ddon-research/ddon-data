using System;
using UnityEngine;
using UnityEngine.UI;

public class ListedLabel : MonoBehaviour
{
	[SerializeField]
	private Text Year;

	[SerializeField]
	private Text Date;

	[SerializeField]
	private Text Time;

	public void UpdateContent(DateTime date)
	{
		Year.text = date.Year.ToString();
		Date.text = date.ToString("M/d");
		Time.text = date.ToString("HH:mm");
	}
}
