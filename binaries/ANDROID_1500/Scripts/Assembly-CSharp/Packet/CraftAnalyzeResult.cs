using System;
using DDOAppMaster.Enum.Craft;

namespace Packet;

[Serializable]
public class CraftAnalyzeResult
{
	public CraftSkillType CraftType;

	public float Value1;

	public uint Value2;
}
