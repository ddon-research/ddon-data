using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using UnityEngine;

public class RegexHypertext : HypertextBase
{
	private struct Entry
	{
		public string RegexPattern;

		public Color Color;

		public Action<string> OnClick;

		public Entry(string regexPattern, Color color, Action<string> onClick)
		{
			RegexPattern = regexPattern;
			Color = color;
			OnClick = onClick;
		}
	}

	private readonly Dictionary<string, Entry> _entryTable = new Dictionary<string, Entry>();

	public void SetClickableByRegex(string regexPattern, Action<string> onClick)
	{
		SetClickableByRegex(regexPattern, color, onClick);
	}

	public void SetClickableByRegex(string regexPattern, Color color, Action<string> onClick)
	{
		if (!string.IsNullOrEmpty(regexPattern) && onClick != null)
		{
			_entryTable[regexPattern] = new Entry(regexPattern, color, onClick);
		}
	}

	public override void RemoveClickable()
	{
		base.RemoveClickable();
		_entryTable.Clear();
	}

	protected override void RegisterClickable()
	{
		foreach (Entry value in _entryTable.Values)
		{
			foreach (Match item in Regex.Matches(text, value.RegexPattern))
			{
				RegisterClickable(item.Index, item.Value.Length, value.Color, value.OnClick);
			}
		}
	}
}
