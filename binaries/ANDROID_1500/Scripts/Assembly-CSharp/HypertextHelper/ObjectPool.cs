using System;
using System.Collections.Generic;
using UnityEngine;

namespace HypertextHelper;

public class ObjectPool<T> where T : new()
{
	private readonly Stack<T> _stack = new Stack<T>();

	private readonly Action<T> _onGet;

	private readonly Action<T> _onRelease;

	public int CountAll { get; set; }

	public int CountActive => CountAll - CountInactive;

	public int CountInactive => _stack.Count;

	public ObjectPool(Action<T> onGet, Action<T> onRelease)
	{
		_onGet = onGet;
		_onRelease = onRelease;
	}

	public T Get()
	{
		T val;
		if (_stack.Count == 0)
		{
			val = new T();
			CountAll++;
		}
		else
		{
			val = _stack.Pop();
		}
		if (_onGet != null)
		{
			_onGet(val);
		}
		return val;
	}

	public void Release(T element)
	{
		if (_stack.Count > 0 && object.ReferenceEquals(_stack.Peek(), element))
		{
			Debug.LogError("Internal error. Trying to destroy object that is already released to pool.");
		}
		if (_onRelease != null)
		{
			_onRelease(element);
		}
		_stack.Push(element);
	}
}
