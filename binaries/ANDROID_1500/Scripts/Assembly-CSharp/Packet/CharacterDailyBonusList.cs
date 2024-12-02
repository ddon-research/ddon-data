using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class CharacterDailyBonusList
{
	public List<CharacterDailyBonus> Bonus = new List<CharacterDailyBonus>();
}
