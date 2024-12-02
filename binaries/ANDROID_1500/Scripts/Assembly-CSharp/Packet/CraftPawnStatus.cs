using System;

namespace Packet;

[Serializable]
public class CraftPawnStatus
{
	public uint MyPawnID;

	public string PawnName;

	public ItemData ProductItem = new ItemData();

	public uint CraftLv;

	public long RemainTime;

	public uint RecipeID;

	public long FinishTime;
}
