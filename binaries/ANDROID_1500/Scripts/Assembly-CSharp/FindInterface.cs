using System;
using UnityEngine;
using UnityEngine.EventSystems;

public static class FindInterface
{
	public static void DoParentEventSystemHandler<T>(this Transform self, Action<T> action) where T : IEventSystemHandler
	{
		Transform parent = self.transform.parent;
		while (parent != null)
		{
			Component[] components = parent.GetComponents<Component>();
			foreach (Component component in components)
			{
				if (component is T)
				{
					action((T)(IEventSystemHandler)component);
				}
			}
			parent = parent.parent;
		}
	}
}
