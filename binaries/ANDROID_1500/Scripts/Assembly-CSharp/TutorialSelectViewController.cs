using System.Collections.Generic;
using UnityEngine;

public class TutorialSelectViewController : ViewController
{
	[SerializeField]
	private TutorialSelectViewCell Cell;

	private List<TutorialSelectViewCell> m_CellList = new List<TutorialSelectViewCell>();

	private void OnEnable()
	{
		Dictionary<TutorialManager.TutorialType, TutorialManager.TutorialData> tutorials = SingletonMonoBehaviour<TutorialManager>.Instance.Tutorials;
		foreach (TutorialSelectViewCell cell in m_CellList)
		{
			cell.gameObject.SetActive(value: false);
		}
		int num = 0;
		foreach (KeyValuePair<TutorialManager.TutorialType, TutorialManager.TutorialData> item in tutorials)
		{
			if (m_CellList.Count <= num)
			{
				TutorialSelectViewCell tutorialSelectViewCell = Object.Instantiate(Cell);
				tutorialSelectViewCell.GetComponent<RectTransform>().SetParent(Cell.transform.parent, worldPositionStays: false);
				tutorialSelectViewCell.GetComponent<RectTransform>().SetAsLastSibling();
				tutorialSelectViewCell.gameObject.SetActive(value: true);
				tutorialSelectViewCell.Setup(item.Key, item.Value);
				m_CellList.Add(tutorialSelectViewCell);
			}
			else
			{
				m_CellList[num].gameObject.SetActive(value: true);
				m_CellList[num].Setup(item.Key, item.Value);
			}
			num++;
		}
	}
}
