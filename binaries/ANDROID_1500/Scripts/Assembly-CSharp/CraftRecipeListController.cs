using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class CraftRecipeListController : MonoBehaviour
{
	public class DDOptionExtend : Dropdown.OptionData
	{
		public CraftMainCategory MainCategoryID;

		public uint SubCategoryID;
	}

	[SerializeField]
	private ProductItemTableViewController TableView;

	[SerializeField]
	private ToggleGroup MainCateogryToggleGroup;

	[SerializeField]
	private Dropdown SubCategoryDD;

	[SerializeField]
	private Text EmptyText;

	private void OnEnable()
	{
		SingletonMonoBehaviour<TutorialManager>.Instance.StartTutorial(TutorialManager.TutorialType.TUTORIAL_ITEM_CREATE);
		if (TableView.IsContents)
		{
			EmptyText.enabled = false;
		}
		else
		{
			EmptyText.enabled = true;
		}
	}

	public void OnClickWeapon(bool isOn)
	{
		if (isOn)
		{
			OnClick(CraftMainCategory.Weapon);
		}
	}

	public void OnClickProtector(bool isOn)
	{
		if (isOn)
		{
			OnClick(CraftMainCategory.Protection);
		}
	}

	public void OnClickUseItem(bool isOn)
	{
		if (isOn)
		{
			OnClick(CraftMainCategory.UseItem);
		}
	}

	public void OnClickMaterialItem(bool isOn)
	{
		if (isOn)
		{
			OnClick(CraftMainCategory.MaterialItem);
		}
	}

	private void OnClick(CraftMainCategory mainCategory)
	{
		TableView.Initialize();
		SubCategoryDD.options.Clear();
		DDOptionExtend dDOptionExtend = new DDOptionExtend();
		dDOptionExtend.text = "未選択";
		SubCategoryDD.options.Add(dDOptionExtend);
		SubCategoryDD.RefreshShownValue();
		SubCategoryDD.value = 0;
		EmptyText.enabled = true;
		StartCoroutine(Craft.GetSubCategory(delegate(CraftCategoryList ret)
		{
			foreach (CraftCategory category in ret.Categories)
			{
				DDOptionExtend item = new DDOptionExtend
				{
					MainCategoryID = mainCategory,
					SubCategoryID = category.ID,
					text = category.Name
				};
				SubCategoryDD.options.Add(item);
			}
		}, null, (uint)mainCategory, CacheOption.OneDay, LoadingAnimation.Default));
	}

	public void OnValueChangedSubCategory(int index)
	{
		DDOptionExtend dDOptionExtend = SubCategoryDD.options[index] as DDOptionExtend;
		if (index > 0)
		{
			TableView.LoadData(dDOptionExtend.MainCategoryID, dDOptionExtend.SubCategoryID);
			EmptyText.enabled = false;
		}
		else
		{
			EmptyText.enabled = true;
		}
	}
}
