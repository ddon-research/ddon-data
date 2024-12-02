using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(ScrollRect))]
public class TableViewController<T> : ViewController
{
	protected List<T> TableData = new List<T>();

	[SerializeField]
	private RectOffset Padding;

	[SerializeField]
	private float SpacingHeight = 4f;

	private RectTransform CellBaseRect;

	private ScrollRect _CachedScrollRect;

	[SerializeField]
	private RectTransform CellContent;

	[SerializeField]
	protected GameObject CellBase;

	protected LinkedList<TableViewCell<T>> cells = new LinkedList<TableViewCell<T>>();

	private Rect visibleRect = default(Rect);

	[SerializeField]
	private RectOffset visibleRectPadding;

	[SerializeField]
	private float ContentOssetY;

	private Vector2 prevScrollPos;

	public ScrollRect CachedScrollRect
	{
		get
		{
			if (_CachedScrollRect == null)
			{
				_CachedScrollRect = GetComponent<ScrollRect>();
			}
			return _CachedScrollRect;
		}
	}

	public void Initialize()
	{
		foreach (TableViewCell<T> cell in cells)
		{
			Object.Destroy(cell.gameObject);
		}
		cells.Clear();
		TableData.Clear();
		Vector2 anchoredPosition = CachedScrollRect.content.anchoredPosition;
		anchoredPosition.y = 0f;
		CachedScrollRect.content.anchoredPosition = anchoredPosition;
		UpdateContents();
		CachedScrollRect.Rebuild(CanvasUpdate.Layout);
	}

	protected virtual void Awake()
	{
		CellBaseRect = CellBase.GetComponent<RectTransform>();
	}

	private void OnEnable()
	{
	}

	protected virtual float CellHeightAtIndex(int index)
	{
		if (CellBaseRect == null)
		{
			CellBaseRect = CellBase.GetComponent<RectTransform>();
		}
		return CellBaseRect.rect.height;
	}

	protected void UpdateContentSize()
	{
		float num = 0f;
		for (int i = 0; i < TableData.Count; i++)
		{
			num += CellHeightAtIndex(i);
			if (i > 0)
			{
				num += SpacingHeight;
			}
		}
		RectTransform rectTransform = CellContent;
		if (rectTransform == null)
		{
			rectTransform = CachedScrollRect.content;
		}
		Vector2 sizeDelta = rectTransform.sizeDelta;
		sizeDelta.y = (float)Padding.top + num + (float)Padding.bottom;
		rectTransform.sizeDelta = sizeDelta;
	}

	protected virtual void Start()
	{
		CellBase.SetActive(value: false);
		CachedScrollRect.onValueChanged.AddListener(OnScrollPosChanged);
	}

	protected virtual GameObject CreateCell(int index)
	{
		return Object.Instantiate(CellBase);
	}

	private TableViewCell<T> CreateCellForIndex(int index)
	{
		GameObject gameObject = CreateCell(index);
		gameObject.SetActive(value: true);
		TableViewCell<T> component = gameObject.GetComponent<TableViewCell<T>>();
		Vector3 localScale = component.transform.localScale;
		Vector2 sizeDelta = component.CachedRectTransform.sizeDelta;
		Vector2 offsetMin = component.CachedRectTransform.offsetMin;
		Vector2 offsetMax = component.CachedRectTransform.offsetMax;
		component.transform.SetParent(CellBase.transform.parent);
		component.transform.localScale = localScale;
		component.CachedRectTransform.sizeDelta = sizeDelta;
		component.CachedRectTransform.offsetMin = offsetMin;
		component.CachedRectTransform.offsetMax = offsetMax;
		UpdateCellForIndex(component, index);
		cells.AddLast(component);
		return component;
	}

	protected virtual void OnViewLastCell()
	{
	}

	private void UpdateCellForIndex(TableViewCell<T> cell, int index)
	{
		cell.DataIndex = index;
		if (cell.DataIndex >= 0 && cell.DataIndex <= TableData.Count - 1)
		{
			cell.gameObject.SetActive(value: true);
			cell.UpdateContent(TableData[cell.DataIndex]);
			cell.Height = CellHeightAtIndex(cell.DataIndex);
			if (cell.DataIndex == TableData.Count - 1)
			{
				OnViewLastCell();
			}
		}
		else
		{
			cell.gameObject.SetActive(value: false);
		}
	}

	private void UpdateVisibleRect()
	{
		visibleRect.x = CachedScrollRect.content.anchoredPosition.x + (float)visibleRectPadding.left;
		visibleRect.y = 0f - CachedScrollRect.content.anchoredPosition.y + (float)visibleRectPadding.top;
		visibleRect.width = base.CachedRectTransform.rect.width + (float)visibleRectPadding.left + (float)visibleRectPadding.right;
		visibleRect.height = base.CachedRectTransform.rect.height + (float)visibleRectPadding.top + (float)visibleRectPadding.bottom;
		if (CellContent != null)
		{
			visibleRect.y += ContentOssetY;
		}
	}

	protected void UpdateContents()
	{
		UpdateContentSize();
		UpdateVisibleRect();
		if (cells.Count < 1)
		{
			Vector2 vector = new Vector2(0f, -Padding.top);
			for (int i = 0; i < TableData.Count; i++)
			{
				float num = CellHeightAtIndex(i);
				Vector2 vector2 = vector + new Vector2(0f, 0f - num);
				if ((vector.y <= visibleRect.y && vector.y >= visibleRect.y - visibleRect.height) || (vector2.y <= visibleRect.y && vector2.y >= visibleRect.y - visibleRect.height))
				{
					TableViewCell<T> tableViewCell = CreateCellForIndex(i);
					tableViewCell.Top = vector;
					break;
				}
				vector = vector2 + new Vector2(0f, SpacingHeight);
			}
			FillVisibleRectWithCells();
		}
		else
		{
			LinkedListNode<TableViewCell<T>> first = cells.First;
			UpdateCellForIndex(first.Value, first.Value.DataIndex);
			for (first = first.Next; first != null; first = first.Next)
			{
				UpdateCellForIndex(first.Value, first.Previous.Value.DataIndex + 1);
				first.Value.Top = first.Previous.Value.Bottom + new Vector2(0f, 0f - SpacingHeight);
			}
			FillVisibleRectWithCells();
		}
	}

	private void FillVisibleRectWithCells()
	{
		if (cells.Count >= 1)
		{
			TableViewCell<T> value = cells.Last.Value;
			int num = value.DataIndex + 1;
			Vector2 top = value.Bottom + new Vector2(0f, 0f - SpacingHeight);
			while (num < TableData.Count && top.y >= visibleRect.y - visibleRect.height)
			{
				TableViewCell<T> tableViewCell = CreateCellForIndex(num);
				tableViewCell.Top = top;
				value = tableViewCell;
				num = value.DataIndex + 1;
				top = value.Bottom + new Vector2(0f, 0f - SpacingHeight);
			}
		}
	}

	public void OnScrollPosChanged(Vector2 scrollPos)
	{
		UpdateVisibleRect();
		ReuseCells((scrollPos.y < prevScrollPos.y) ? 1 : (-1));
		prevScrollPos = scrollPos;
	}

	private void ReuseCells(int scrollDirection)
	{
		if (cells.Count < 1)
		{
			return;
		}
		if (scrollDirection > 0)
		{
			TableViewCell<T> value = cells.First.Value;
			while (value.Bottom.y > visibleRect.y + (float)Padding.bottom)
			{
				TableViewCell<T> value2 = cells.Last.Value;
				UpdateCellForIndex(value, value2.DataIndex + 1);
				value.Top = value2.Bottom + new Vector2(0f, 0f - SpacingHeight);
				cells.AddLast(value);
				cells.RemoveFirst();
				value = cells.First.Value;
			}
			FillVisibleRectWithCells();
		}
		else if (scrollDirection < 0)
		{
			TableViewCell<T> value3 = cells.Last.Value;
			while (value3.Top.y < visibleRect.y - visibleRect.height)
			{
				TableViewCell<T> value4 = cells.First.Value;
				UpdateCellForIndex(value3, value4.DataIndex - 1);
				value3.Bottom = value4.Top + new Vector2(0f, SpacingHeight);
				cells.AddFirst(value3);
				cells.RemoveLast();
				value3 = cells.Last.Value;
			}
		}
	}
}
