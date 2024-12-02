using UnityEngine;
using UnityEngine.Events;

public class CustomMenuContentData
{
	public Color TextColor = Color.black;

	public string Name { get; set; }

	public UnityAction OnClick { get; set; }

	public bool IsBorder { get; set; }
}
