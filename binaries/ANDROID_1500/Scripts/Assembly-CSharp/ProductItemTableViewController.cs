using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

[RequireComponent(typeof(ScrollRect))]
public class ProductItemTableViewController : TableViewController<CraftRecipe>
{
	public bool IsContents => TableData.Count > 0;

	public void LoadData(CraftMainCategory mainCategory, uint subCategory)
	{
		Initialize();
		StartCoroutine(Craft.GetRecipeList(delegate(CraftRecipeList ret)
		{
			foreach (CraftRecipe recipe in ret.Recipes)
			{
				TableData.Add(recipe);
			}
			UpdateContents();
		}, null, (uint)mainCategory, subCategory, CacheOption.OneHour, LoadingAnimation.Default));
	}
}
