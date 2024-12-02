using System;
using System.Collections.Generic;
using UnityEngine;

public class iTweenEventHandler : MonoBehaviour
{
	public enum ANIMATION_TYPE
	{
		MOVE_TO,
		FADE_TO,
		FADE_FROM,
		SCALE_TO,
		SCALE_FROM,
		PUNCH_POS
	}

	public Dictionary<ANIMATION_TYPE, Action> OnCompleteDelegate = new Dictionary<ANIMATION_TYPE, Action>();

	public Action<Vector2> OnUpdateMoveDelegate { get; set; }

	public Action<float> OnUpdateAlphaDelegate { get; set; }

	public void OnUpdateMove(Vector2 value)
	{
		if (OnUpdateMoveDelegate != null)
		{
			OnUpdateMoveDelegate(value);
		}
	}

	public void OnUpdateAlpha(float value)
	{
		if (OnUpdateAlphaDelegate != null)
		{
			OnUpdateAlphaDelegate(value);
		}
	}

	public void OnComplete(ANIMATION_TYPE type)
	{
		if (OnCompleteDelegate.ContainsKey(type))
		{
			OnCompleteDelegate[type]?.Invoke();
		}
	}
}
