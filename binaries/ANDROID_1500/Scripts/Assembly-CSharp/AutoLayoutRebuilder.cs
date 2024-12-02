using System;
using UnityEngine;
using UnityEngine.UI;

public class AutoLayoutRebuilder : MonoBehaviour
{
	[SerializeField]
	private bool IsLoaded;

	[SerializeField]
	private bool IsLayouted;

	[SerializeField]
	private GameObject[] LayoutList;

	private Action BuiltCallback;

	private void Update()
	{
		RebuildUpdate();
	}

	public void RebuildUpdate()
	{
		if (IsLayouted || !IsLoaded)
		{
			return;
		}
		GameObject[] layoutList = LayoutList;
		foreach (GameObject gameObject in layoutList)
		{
			if (!(gameObject == null))
			{
				LayoutRebuilder.ForceRebuildLayoutImmediate(gameObject.transform as RectTransform);
			}
		}
		if (BuiltCallback != null)
		{
			BuiltCallback();
			BuiltCallback = null;
		}
		IsLayouted = true;
	}

	public void MarkRebuild(Action callback)
	{
		IsLoaded = true;
		IsLayouted = false;
		BuiltCallback = callback;
	}

	public void MarkRebuild()
	{
		IsLoaded = true;
		IsLayouted = false;
		BuiltCallback = null;
	}
}
