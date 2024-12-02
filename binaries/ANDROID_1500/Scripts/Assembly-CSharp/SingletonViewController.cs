using UnityEngine;

public class SingletonViewController<T> : ViewController where T : ViewController
{
	private static T instance;

	public static T Instance
	{
		get
		{
			if (instance == null)
			{
				instance = (T)Object.FindObjectOfType(typeof(T));
				if (instance == null)
				{
					Debug.LogError(string.Concat(typeof(T), "is nothing"));
				}
			}
			return instance;
		}
	}

	protected void Awake()
	{
		CheckInstance();
	}

	protected bool CheckInstance()
	{
		if (this == Instance)
		{
			return true;
		}
		Object.Destroy(this);
		return false;
	}
}
