using System.Globalization;
using UnityEngine;
using UnityEngine.UI;

public class TopPageScheduleListBoxElement : ListBoxElement<TopPageScheduleData>
{
	[SerializeField]
	private Text DateLabel;

	[SerializeField]
	private Text NameLabel;

	public override void UpdateContent(TopPageScheduleData itemData)
	{
		DateLabel.text = itemData.Date.ToString("M月d日(ddd)", CultureInfo.GetCultureInfo("ja-JP"));
		NameLabel.text = itemData.Name;
	}
}
