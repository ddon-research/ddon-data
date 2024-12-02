using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;

public class CacheManager : SingletonMonoBehaviour<CacheManager>
{
	private Dictionary<Type, CacheBase> CacheDic = new Dictionary<Type, CacheBase>();

	public IEnumerator Initialize()
	{
		Assembly asm = Assembly.GetEntryAssembly();
		IEnumerable<Type> types = from t in asm.GetTypes()
			where t.IsSubclassOf(typeof(CacheBase))
			select t;
		foreach (Type type in types)
		{
			CacheBase cache = Activator.CreateInstance(type) as CacheBase;
			yield return cache.Initialize();
			CacheDic.Add(type, cache);
		}
	}

	public T GetCache<T>() where T : CacheBase
	{
		return (T)CacheDic[typeof(T)];
	}
}
