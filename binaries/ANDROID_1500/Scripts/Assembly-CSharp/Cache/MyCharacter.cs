using System.Collections;
using Packet;
using WebRequest;

namespace Cache;

public class MyCharacter : CacheBase
{
	public CharacterDataBase Base { get; set; }

	public CharacterDataDetail Detail { get; set; }

	public override IEnumerator OnInitialize()
	{
		yield return CharacterData.GetBase(delegate(CharacterDataBase result)
		{
			Base = result;
		}, null);
	}
}
