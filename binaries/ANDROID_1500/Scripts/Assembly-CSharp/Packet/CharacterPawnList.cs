using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class CharacterPawnList
{
	public List<CharacterPawn> MainPawnList = new List<CharacterPawn>();

	public List<CharacterPawn> SupportPawnList = new List<CharacterPawn>();
}
