using System;
using DDOAppMaster.Enum.Craft;

namespace Packet;

[Serializable]
public class CraftSkillLevel
{
	public CraftSkillType CraftType;

	public uint Level;
}
