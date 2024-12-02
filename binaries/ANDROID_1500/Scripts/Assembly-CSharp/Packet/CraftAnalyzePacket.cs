using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class CraftAnalyzePacket
{
	public List<CraftPawnParam> MainPawnInfoList = new List<CraftPawnParam>();

	public List<CraftPawnParam> AssistPawnInfoList = new List<CraftPawnParam>();

	public uint ToppingItemId;

	public uint RecipeId;
}
