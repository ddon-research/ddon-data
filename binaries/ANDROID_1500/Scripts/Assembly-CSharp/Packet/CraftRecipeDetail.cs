using System.Collections.Generic;

namespace Packet;

public class CraftRecipeDetail
{
	public uint RecipeID;

	public ItemData ProductItem = new ItemData();

	public uint ProductNum;

	public uint TimeSeconds;

	public uint Const;

	public uint Exp;

	public List<CraftRecipeMaterial> Materials = new List<CraftRecipeMaterial>();

	public byte MaxCraftNum;

	public bool CanUseRefine;
}
