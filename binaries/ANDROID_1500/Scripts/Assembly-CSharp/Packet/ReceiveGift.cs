using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class ReceiveGift
{
	public bool IsReceive;

	public List<CharacterGift> Gift = new List<CharacterGift>();

	public CharacterJemList Jem = new CharacterJemList();
}
