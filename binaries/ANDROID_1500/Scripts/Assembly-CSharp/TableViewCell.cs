using UnityEngine;

public class TableViewCell<T> : ViewController
{
	public int DataIndex { get; set; }

	public float Height
	{
		get
		{
			return base.CachedRectTransform.sizeDelta.y;
		}
		set
		{
			Vector2 sizeDelta = base.CachedRectTransform.sizeDelta;
			sizeDelta.y = value;
			base.CachedRectTransform.sizeDelta = sizeDelta;
		}
	}

	public Vector2 Top
	{
		get
		{
			Vector3[] array = new Vector3[4];
			base.CachedRectTransform.GetLocalCorners(array);
			return base.CachedRectTransform.anchoredPosition + new Vector2(0f, array[1].y);
		}
		set
		{
			Vector3[] array = new Vector3[4];
			base.CachedRectTransform.GetLocalCorners(array);
			base.CachedRectTransform.anchoredPosition = value - new Vector2(0f, array[1].y);
		}
	}

	public Vector2 Bottom
	{
		get
		{
			Vector3[] array = new Vector3[4];
			base.CachedRectTransform.GetLocalCorners(array);
			return base.CachedRectTransform.anchoredPosition + new Vector2(0f, array[3].y);
		}
		set
		{
			Vector3[] array = new Vector3[4];
			base.CachedRectTransform.GetLocalCorners(array);
			base.CachedRectTransform.anchoredPosition = value - new Vector2(0f, array[3].y);
		}
	}

	public virtual void UpdateContent(T itemData)
	{
	}
}
