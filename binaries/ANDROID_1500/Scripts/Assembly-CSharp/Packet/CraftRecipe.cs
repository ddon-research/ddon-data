using System;

namespace Packet;

[Serializable]
public class CraftRecipe
{
	public uint MainCategoryID;

	public uint RecipeID;

	public ItemData ProductItem = new ItemData();

	public uint ProductNum;

	public uint TimeSeconds;

	public uint Const;

	public uint Exp;
}
