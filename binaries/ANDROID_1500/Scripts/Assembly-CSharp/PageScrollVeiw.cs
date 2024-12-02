using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

public class PageScrollVeiw : ScrollRect
{
	public float SlideValue = 5f;

	public float SlideMove = 3000f;

	public Button LeftButton;

	public Button RightButton;

	public Text PageNumText;

	public bool IsSlide = true;

	public bool IsDrag = true;

	private float m_PageWidth;

	private int m_PrevPageIndex;

	private int m_PageNum;

	private Vector2 m_TargetPos;

	private bool mIsDrag;

	public int PageNum => m_PageNum;

	public int CurrentPage => m_PrevPageIndex;

	protected override void Awake()
	{
		base.Awake();
		SetupPage();
	}

	protected void Update()
	{
		if (m_TargetPos != base.content.anchoredPosition && !mIsDrag)
		{
			float sqrMagnitude = (m_TargetPos - base.content.anchoredPosition).sqrMagnitude;
			float num = SlideMove * Time.deltaTime;
			if (sqrMagnitude <= num * num || !IsSlide)
			{
				base.content.anchoredPosition = m_TargetPos;
			}
			else
			{
				base.content.anchoredPosition += (m_TargetPos - base.content.anchoredPosition).normalized * num;
			}
		}
	}

	public override void OnBeginDrag(PointerEventData eventData)
	{
		if (IsDrag)
		{
			base.OnBeginDrag(eventData);
			mIsDrag = true;
		}
	}

	public override void OnEndDrag(PointerEventData eventData)
	{
		if (!IsDrag)
		{
			return;
		}
		base.OnEndDrag(eventData);
		mIsDrag = false;
		StopMovement();
		int num = -Mathf.RoundToInt(base.content.anchoredPosition.x / m_PageWidth);
		if (num == m_PrevPageIndex && Mathf.Abs(eventData.delta.x) >= SlideValue)
		{
			num -= (int)Mathf.Sign(eventData.delta.x);
			if (num < 0 || num >= m_PageNum)
			{
				num = m_PrevPageIndex;
			}
		}
		float x = (float)(-num) * m_PageWidth;
		m_TargetPos = new Vector2(x, base.content.anchoredPosition.y);
		m_PrevPageIndex = num;
		UpdateButton();
	}

	public void OnLeftPush()
	{
		if (m_PrevPageIndex > 0)
		{
			m_PrevPageIndex--;
			float x = (float)(-m_PrevPageIndex) * m_PageWidth;
			m_TargetPos = new Vector2(x, base.content.anchoredPosition.y);
			UpdateButton();
		}
		else if (!IsSlide)
		{
			m_PrevPageIndex = m_PageNum - 1;
			float x2 = (float)(-m_PrevPageIndex) * m_PageWidth;
			m_TargetPos = new Vector2(x2, base.content.anchoredPosition.y);
			UpdateButton();
		}
	}

	public void OnRightPush()
	{
		if (m_PrevPageIndex < m_PageNum - 1)
		{
			m_PrevPageIndex++;
			float x = (float)(-m_PrevPageIndex) * m_PageWidth;
			m_TargetPos = new Vector2(x, base.content.anchoredPosition.y);
			UpdateButton();
		}
		else if (!IsSlide)
		{
			m_PrevPageIndex = 0;
			float x2 = (float)(-m_PrevPageIndex) * m_PageWidth;
			m_TargetPos = new Vector2(x2, base.content.anchoredPosition.y);
			UpdateButton();
		}
	}

	private void UpdateButton()
	{
		if (LeftButton != null)
		{
			if (m_PrevPageIndex <= 0)
			{
				LeftButton.interactable = false;
			}
			else
			{
				LeftButton.interactable = true;
			}
		}
		if (RightButton != null)
		{
			if (m_PrevPageIndex >= m_PageNum - 1)
			{
				RightButton.interactable = false;
			}
			else
			{
				RightButton.interactable = true;
			}
		}
		if (PageNumText != null)
		{
			PageNumText.text = m_PrevPageIndex + 1 + " / " + m_PageNum;
		}
	}

	public void ResetPage()
	{
		m_PrevPageIndex = 0;
		float x = (float)(-m_PrevPageIndex) * m_PageWidth;
		m_TargetPos = new Vector2(x, base.content.anchoredPosition.y);
		base.content.anchoredPosition = m_TargetPos;
		UpdateButton();
	}

	public void SetupPage()
	{
		GridLayoutGroup component = base.content.GetComponent<GridLayoutGroup>();
		m_PageWidth = component.cellSize.x + component.spacing.x;
		m_PageNum = 0;
		for (int i = 0; i < base.content.childCount; i++)
		{
			if (base.content.GetChild(i).gameObject.activeSelf)
			{
				m_PageNum++;
			}
		}
		base.content.GetComponent<RectTransform>().sizeDelta = new Vector2(m_PageWidth * (float)m_PageNum, component.cellSize.y);
		m_TargetPos = base.content.anchoredPosition;
		ResetPage();
	}
}
