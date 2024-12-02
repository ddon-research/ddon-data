using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class CraftPawn
{
	public uint MyPawnID;

	public string Name;

	public bool CanCraft;

	public long RemainTime;

	public ushort CraftCount;

	public ushort CraftRank;

	public uint NowExp;

	public uint NaxtExp;

	public List<CraftSkillLevel> SkillLevelList = new List<CraftSkillLevel>();
}
