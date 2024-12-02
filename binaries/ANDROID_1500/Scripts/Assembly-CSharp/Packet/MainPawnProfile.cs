using System;

namespace Packet;

[Serializable]
public class MainPawnProfile
{
	public PawnProfileData Profile = new PawnProfileData();

	public byte JobID;

	public ushort JobLv;

	public string JobName;

	public uint ItemRank;

	public uint Present;

	public ushort CraftLv;

	public ushort CraftSpeed;

	public ushort CraftCreateNum;

	public ushort CraftEquip;

	public ushort CraftCost;

	public ushort CraftQuality;

	public uint RentalCost;
}
