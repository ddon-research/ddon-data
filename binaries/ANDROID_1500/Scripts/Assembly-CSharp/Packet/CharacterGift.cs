using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class CharacterGift
{
	public uint Id;

	public string Text;

	public List<CharacterGiftJem> Jems = new List<CharacterGiftJem>();

	public long Expire;
}
