using System.Collections;

public class CacheBase
{
	public bool IsInitialize { get; private set; }

	public IEnumerator Initialize()
	{
		IsInitialize = false;
		yield return OnInitialize();
		IsInitialize = true;
	}

	public virtual IEnumerator OnInitialize()
	{
		yield return null;
	}
}
