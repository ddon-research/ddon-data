using System;
using UnityEngine;

[AttributeUsage(AttributeTargets.Method)]
public class EnumActionAttribute : PropertyAttribute
{
	public Type enumType;

	public EnumActionAttribute(Type enumType)
	{
		this.enumType = enumType;
	}
}
