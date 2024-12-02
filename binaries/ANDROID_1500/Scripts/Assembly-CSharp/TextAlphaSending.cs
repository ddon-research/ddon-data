using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class TextAlphaSending : BaseMeshEffect
{
	public float Speed = 1f;

	private const int OneSpriteVertex = 6;

	private bool _isEnd;

	private float _alpha;

	private int _charaCount;

	private Text _text;

	public Text Text => _text ?? (_text = GetComponent<Text>());

	public bool IsEnd()
	{
		return _isEnd;
	}

	public void FlushAll()
	{
		_charaCount = Text.text.Length;
	}

	public void Initialize()
	{
		_charaCount = 0;
		_isEnd = false;
	}

	public override void ModifyMesh(VertexHelper vh)
	{
		List<UIVertex> list = new List<UIVertex>();
		List<UIVertex> list2 = new List<UIVertex>();
		Text text = Text;
		vh.GetUIVertexStream(list);
		int num = _charaCount * 6;
		if (num >= list.Count)
		{
			_isEnd = true;
			return;
		}
		for (int i = 0; i < num; i++)
		{
			list2.Add(list[i]);
		}
		for (int j = num; j < num + 6; j++)
		{
			UIVertex item = list[j];
			item.color.a = (byte)(255f * _alpha);
			list2.Add(item);
		}
		_alpha += Time.deltaTime * Speed;
		if (_alpha >= 1f)
		{
			_charaCount++;
			_alpha = 0f;
		}
		vh.Clear();
		vh.AddUIVertexTriangleStream(list2);
	}
}
