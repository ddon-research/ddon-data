using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class GiftMasterData
{
	public uint GiftId;

	public string Text;

	public List<CharacterGiftJem> Jems = new List<CharacterGiftJem>();
}
