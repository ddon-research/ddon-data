using System.Collections.Generic;
using DDOAppMaster.Enum.Craft;

public class CraftpawnData
{
	public uint MyPawnID;

	public string PawnName;

	public ushort CraftLv;

	public uint NowExp;

	public uint NextExp;

	public bool IsMyPawn;

	public uint Limit;

	public bool CanCraft;

	public long RemainTime;

	public Dictionary<CraftSkillType, uint> SkillLvs = new Dictionary<CraftSkillType, uint>();
}
