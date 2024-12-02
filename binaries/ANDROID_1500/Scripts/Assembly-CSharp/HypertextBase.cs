using System;
using System.Collections.Generic;
using HypertextHelper;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

public abstract class HypertextBase : Text, IPointerClickHandler, IEventSystemHandler
{
	private struct ClickableEntry
	{
		public string Word;

		public int StartIndex;

		public Color Color;

		public Action<string> OnClick;

		public List<Rect> Rects;

		public ClickableEntry(string word, int startIndex, Color color, Action<string> onClick)
		{
			Word = word;
			StartIndex = startIndex;
			Color = color;
			OnClick = onClick;
			Rects = new List<Rect>();
		}
	}

	private Canvas _rootCanvas;

	private const int CharVertsNum = 6;

	private readonly List<ClickableEntry> _entries = new List<ClickableEntry>();

	private static readonly ObjectPool<List<UIVertex>> _verticesPool = new ObjectPool<List<UIVertex>>(null, delegate(List<UIVertex> l)
	{
		l.Clear();
	});

	private Canvas RootCanvas => _rootCanvas ?? (_rootCanvas = GetComponentInParent<Canvas>());

	protected void RegisterClickable(int startIndex, int wordLength, Color color, Action<string> onClick)
	{
		if (onClick != null && startIndex >= 0 && wordLength >= 0 && startIndex + wordLength <= text.Length)
		{
			_entries.Add(new ClickableEntry(text.Substring(startIndex, wordLength), startIndex, color, onClick));
		}
	}

	public virtual void RemoveClickable()
	{
		_entries.Clear();
	}

	protected abstract void RegisterClickable();

	protected override void OnPopulateMesh(VertexHelper vertexHelper)
	{
		base.OnPopulateMesh(vertexHelper);
		_entries.Clear();
		RegisterClickable();
		List<UIVertex> vertices = _verticesPool.Get();
		vertexHelper.GetUIVertexStream(vertices);
		Modify(ref vertices);
		vertexHelper.Clear();
		vertexHelper.AddUIVertexTriangleStream(vertices);
		_verticesPool.Release(vertices);
	}

	private void Modify(ref List<UIVertex> vertices)
	{
		int count = vertices.Count;
		int i = 0;
		for (int count2 = _entries.Count; i < count2; i++)
		{
			ClickableEntry value = _entries[i];
			int j = value.StartIndex;
			for (int num = value.StartIndex + value.Word.Length; j < num; j++)
			{
				int num2 = j * 6;
				if (num2 + 6 > count)
				{
					break;
				}
				Vector2 min = Vector2.one * float.MaxValue;
				Vector2 max = Vector2.one * float.MinValue;
				for (int k = 0; k < 6; k++)
				{
					UIVertex value2 = vertices[num2 + k];
					value2.color = value.Color;
					vertices[num2 + k] = value2;
					Vector3 position = vertices[num2 + k].position;
					if (position.y < min.y)
					{
						min.y = position.y;
					}
					if (position.x < min.x)
					{
						min.x = position.x;
					}
					if (position.y > max.y)
					{
						max.y = position.y;
					}
					if (position.x > max.x)
					{
						max.x = position.x;
					}
				}
				value.Rects.Add(new Rect
				{
					min = min,
					max = max
				});
			}
			List<Rect> list = new List<Rect>();
			foreach (List<Rect> item in SplitRectsByRow(value.Rects))
			{
				list.Add(CalculateAABB(item));
			}
			value.Rects = list;
			_entries[i] = value;
		}
	}

	private List<List<Rect>> SplitRectsByRow(List<Rect> rects)
	{
		List<List<Rect>> list = new List<List<Rect>>();
		int num = 0;
		int i = 1;
		for (int count = rects.Count; i < count; i++)
		{
			if (rects[i].xMin < rects[i - 1].xMin)
			{
				list.Add(rects.GetRange(num, i - num));
				num = i;
			}
		}
		if (num < rects.Count)
		{
			list.Add(rects.GetRange(num, rects.Count - num));
		}
		return list;
	}

	private Rect CalculateAABB(List<Rect> rects)
	{
		Vector2 min = Vector2.one * float.MaxValue;
		Vector2 max = Vector2.one * float.MinValue;
		int i = 0;
		for (int count = rects.Count; i < count; i++)
		{
			if (rects[i].xMin < min.x)
			{
				min.x = rects[i].xMin;
			}
			if (rects[i].yMin < min.y)
			{
				min.y = rects[i].yMin;
			}
			if (rects[i].xMax > max.x)
			{
				max.x = rects[i].xMax;
			}
			if (rects[i].yMax > max.y)
			{
				max.y = rects[i].yMax;
			}
		}
		Rect result = default(Rect);
		result.min = min;
		result.max = max;
		return result;
	}

	private Vector3 ToLocalPosition(Vector3 position, Camera camera)
	{
		if (!RootCanvas)
		{
			return Vector3.zero;
		}
		if (RootCanvas.renderMode == RenderMode.ScreenSpaceOverlay)
		{
			return base.transform.InverseTransformPoint(position);
		}
		Vector2 localPoint = Vector2.zero;
		RectTransformUtility.ScreenPointToLocalPointInRectangle(base.rectTransform, position, camera, out localPoint);
		return localPoint;
	}

	void IPointerClickHandler.OnPointerClick(PointerEventData eventData)
	{
		Vector3 point = ToLocalPosition(eventData.position, eventData.pressEventCamera);
		for (int i = 0; i < _entries.Count; i++)
		{
			for (int j = 0; j < _entries[i].Rects.Count; j++)
			{
				if (_entries[i].Rects[j].Contains(point))
				{
					_entries[i].OnClick(_entries[i].Word);
					break;
				}
			}
		}
	}
}
