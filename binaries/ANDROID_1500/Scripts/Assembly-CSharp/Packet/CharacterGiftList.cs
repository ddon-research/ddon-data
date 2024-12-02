using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class CharacterGiftList
{
	public List<CharacterGift> Gift = new List<CharacterGift>();
}
