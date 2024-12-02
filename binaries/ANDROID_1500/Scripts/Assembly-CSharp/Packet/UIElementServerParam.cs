using System;

namespace Packet;

[Serializable]
public class UIElementServerParam
{
	public ulong Param1;

	public ulong Param2;

	public string Text1;

	public string Text2;

	public uint DebugParamByte;

	public uint GetDebugParamByte(uint pos, uint mask = 1u)
	{
		uint debugParamByte = DebugParamByte;
		debugParamByte >>= (int)pos;
		return debugParamByte & mask;
	}
}
