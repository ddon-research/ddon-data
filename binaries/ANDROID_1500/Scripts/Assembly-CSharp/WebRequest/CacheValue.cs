using System;

namespace WebRequest;

internal class CacheValue<T>
{
	public DateTime Expire;

	public T Data;

	public CacheValue()
	{
		Expire = DateTime.Now;
	}
}
