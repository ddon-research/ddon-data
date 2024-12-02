using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class CraftRecipeList
{
	public List<CraftRecipe> Recipes = new List<CraftRecipe>();
}
