using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class PageScrollVeiwPoint : GridLayoutGroup
{
	public GameObject FocusPoint;

	public GameObject DefultPoint;

	private PageScrollVeiw m_Veiw;

	private List<GameObject> m_PointList = new List<GameObject>();

	private int mCurrentPoint;

	protected override void Start()
	{
		base.Start();
		m_Veiw = GetComponentInParent<PageScrollVeiw>();
		if (m_Veiw == null)
		{
			Debug.Log("親コンポーネントにPageScrollVeiwが存在しません");
			return;
		}
		if (m_Veiw.PageNum <= 1)
		{
			DefultPoint.SetActive(value: false);
			return;
		}
		m_PointList.Add(DefultPoint);
		for (int i = 2; i < m_Veiw.PageNum; i++)
		{
			GameObject gameObject = Object.Instantiate(DefultPoint);
			gameObject.GetComponent<RectTransform>().SetParent(DefultPoint.transform.parent, worldPositionStays: false);
			m_PointList.Add(gameObject);
		}
		FocusPoint.GetComponent<RectTransform>().SetAsFirstSibling();
	}

	private void Update()
	{
		if (!(m_Veiw == null) && m_Veiw.PageNum > 1 && mCurrentPoint != m_Veiw.CurrentPage)
		{
			mCurrentPoint = m_Veiw.CurrentPage;
			FocusPoint.GetComponent<RectTransform>().SetAsFirstSibling();
			for (int i = 0; i < mCurrentPoint; i++)
			{
				m_PointList[i].GetComponent<RectTransform>().SetAsFirstSibling();
			}
		}
	}
}
