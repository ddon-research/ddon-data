using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

[RequireComponent(typeof(Button))]
public class ProductItemTableViewCell : TableViewCell<CraftRecipe>
{
	private Button ClickButton;

	[SerializeField]
	private Text Name;

	[SerializeField]
	private Text ItemRank;

	[SerializeField]
	private CraftMaterialSelectController SelectPage;

	[SerializeField]
	private ItemIcon ProductItemIcon;

	public uint RecipeID;

	private CraftRecipe Recipe;

	private void Start()
	{
		ClickButton = GetComponent<Button>();
		ClickButton.onClick.AddListener(OnClick);
	}

	public override void UpdateContent(CraftRecipe itemData)
	{
		Recipe = itemData;
		Name.text = itemData.ProductItem.Name;
		ItemRank.text = itemData.ProductItem.Rank.ToString();
		RecipeID = itemData.RecipeID;
		ProductItemIcon.Load(itemData.ProductItem.IconName, itemData.ProductItem.IconColorId);
	}

	public void OnClick()
	{
		StartCoroutine(Craft.GetRecipeDetail(delegate(CraftRecipeDetail ret)
		{
			SingletonMonoBehaviour<CraftManager>.Instance.Clear();
			SelectPage.RecipeDetail = ret;
			SelectPage.MainCategory = (CraftMainCategory)Recipe.MainCategoryID;
			SelectPage.MaxCraftNum = ret.MaxCraftNum;
			SingletonMonoBehaviour<NavigationViewController>.Instance.Push(SelectPage);
		}, null, RecipeID, CacheOption.OneHour, LoadingAnimation.Default));
	}
}
