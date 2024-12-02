using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class CharacterIDList
{
	public List<uint> CharacterIDs = new List<uint>();
}
