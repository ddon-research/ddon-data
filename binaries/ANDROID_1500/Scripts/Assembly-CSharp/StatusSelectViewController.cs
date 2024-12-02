using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class StatusSelectViewController : ViewController
{
	[SerializeField]
	private StatusSelectViewCell PlayerCell;

	[SerializeField]
	private StatusSelectViewCell MainPawnCell;

	[SerializeField]
	private StatusSelectViewCell SupportPawnCell;

	[SerializeField]
	private GameObject PlayerHeader;

	[SerializeField]
	private GameObject MainPawnHeader;

	[SerializeField]
	private GameObject SupportPawnHeader;

	private List<StatusSelectViewCell> m_MainPawnCells = new List<StatusSelectViewCell>();

	private List<StatusSelectViewCell> m_SupportPawnCells = new List<StatusSelectViewCell>();

	public void Initialize()
	{
		PlayerCell.gameObject.SetActive(value: false);
		MainPawnCell.gameObject.SetActive(value: false);
		SupportPawnCell.gameObject.SetActive(value: false);
		PlayerHeader.SetActive(value: false);
		MainPawnHeader.SetActive(value: false);
		SupportPawnHeader.SetActive(value: false);
		if (m_MainPawnCells != null)
		{
			foreach (StatusSelectViewCell mainPawnCell in m_MainPawnCells)
			{
				mainPawnCell.gameObject.SetActive(value: false);
			}
		}
		if (m_SupportPawnCells == null)
		{
			return;
		}
		foreach (StatusSelectViewCell supportPawnCell in m_SupportPawnCells)
		{
			supportPawnCell.gameObject.SetActive(value: false);
		}
	}

	private void OnEnable()
	{
		if (SingletonMonoBehaviour<NavigationViewController>.Instance.PrevNavigationDir == NavigationViewController.NavigationDir.Back)
		{
			return;
		}
		Initialize();
		StartCoroutine(CharacterData.GetPawnList(delegate(CharacterPawnList res)
		{
			CharacterDataBase characterData = SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData;
			PlayerHeader.SetActive(value: true);
			PlayerCell.gameObject.SetActive(value: true);
			PlayerCell.UpdateContent(characterData.CharacterID, 0u, characterData.FirstName + " " + characterData.LastName);
			if (res.MainPawnList != null && res.MainPawnList.Count > 0)
			{
				MainPawnHeader.SetActive(value: true);
				MainPawnHeader.transform.SetAsLastSibling();
				int num = 0;
				foreach (CharacterPawn mainPawn in res.MainPawnList)
				{
					if (num >= m_MainPawnCells.Count)
					{
						StatusSelectViewCell statusSelectViewCell = Object.Instantiate(MainPawnCell);
						statusSelectViewCell.GetComponent<RectTransform>().SetParent(MainPawnCell.transform.parent, worldPositionStays: false);
						statusSelectViewCell.gameObject.SetActive(value: true);
						statusSelectViewCell.GetComponent<RectTransform>().SetAsLastSibling();
						statusSelectViewCell.UpdateContent(characterData.CharacterID, mainPawn.PawnId, mainPawn.Name);
						m_MainPawnCells.Add(statusSelectViewCell);
					}
					else
					{
						m_MainPawnCells[num].gameObject.SetActive(value: true);
						m_MainPawnCells[num].transform.SetAsLastSibling();
						m_MainPawnCells[num].UpdateContent(characterData.CharacterID, mainPawn.PawnId, mainPawn.Name);
					}
					num++;
				}
			}
			if (res.SupportPawnList != null && res.SupportPawnList.Count > 0)
			{
				SupportPawnHeader.SetActive(value: true);
				SupportPawnHeader.transform.SetAsLastSibling();
				int num2 = 0;
				foreach (CharacterPawn supportPawn in res.SupportPawnList)
				{
					if (num2 >= m_SupportPawnCells.Count)
					{
						StatusSelectViewCell statusSelectViewCell2 = Object.Instantiate(SupportPawnCell);
						statusSelectViewCell2.GetComponent<RectTransform>().SetParent(SupportPawnCell.transform.parent, worldPositionStays: false);
						statusSelectViewCell2.gameObject.SetActive(value: true);
						statusSelectViewCell2.GetComponent<RectTransform>().SetAsLastSibling();
						statusSelectViewCell2.UpdateContent(characterData.CharacterID, supportPawn.PawnId, supportPawn.Name);
						m_SupportPawnCells.Add(statusSelectViewCell2);
					}
					else
					{
						m_SupportPawnCells[num2].gameObject.SetActive(value: true);
						m_SupportPawnCells[num2].transform.SetAsLastSibling();
						m_SupportPawnCells[num2].UpdateContent(characterData.CharacterID, supportPawn.PawnId, supportPawn.Name);
					}
					num2++;
				}
			}
			GetComponent<ScrollRect>().verticalNormalizedPosition = 1f;
		}, null, CacheOption.OneMinute, LoadingAnimation.Default));
	}
}
