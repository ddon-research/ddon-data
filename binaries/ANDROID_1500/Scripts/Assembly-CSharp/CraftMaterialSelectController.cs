using System;
using System.Collections;
using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class CraftMaterialSelectController : ViewController
{
	[SerializeField]
	private new ItemIcon Icon;

	[SerializeField]
	private Text ItemNameText;

	[SerializeField]
	private CraftMaterialTableViewController TableView;

	[SerializeField]
	private Text CostText;

	[SerializeField]
	private Text TimeText;

	[SerializeField]
	private ViewController MakingPage;

	[SerializeField]
	private Button CreateButton;

	[SerializeField]
	private Dropdown CraftNumDD;

	public CraftRecipeDetail RecipeDetail;

	public CraftMainCategory MainCategory;

	public byte MaxCraftNum;

	private void Awake()
	{
		CreateButton.onClick.AddListener(CreateItem);
	}

	private void Update()
	{
		CostText.text = (RecipeDetail.Const * SingletonMonoBehaviour<CraftManager>.Instance.CraftNum).ToString("N0");
		TimeSpan timeSpan = new TimeSpan(0, 0, (int)(RecipeDetail.TimeSeconds * SingletonMonoBehaviour<CraftManager>.Instance.CraftNum));
		TimeText.text = timeSpan.ToString();
		if (SingletonMonoBehaviour<CraftManager>.Instance.IsFillMaterial() != CreateButton.gameObject.activeSelf)
		{
			CreateButton.gameObject.SetActive(SingletonMonoBehaviour<CraftManager>.Instance.IsFillMaterial());
		}
	}

	public void OnEnable()
	{
		SingletonMonoBehaviour<CraftManager>.Instance.MainCategory = MainCategory;
		SingletonMonoBehaviour<CraftManager>.Instance.RecipeDetail = RecipeDetail;
		CraftNumDD.ClearOptions();
		for (byte b = 1; b < MaxCraftNum + 1; b++)
		{
			CraftNumDD.options.Add(new Dropdown.OptionData(b.ToString()));
		}
		if (SingletonMonoBehaviour<CraftManager>.Instance.CraftNum > MaxCraftNum)
		{
			SingletonMonoBehaviour<CraftManager>.Instance.CraftNum = MaxCraftNum;
		}
		CraftNumDD.value = (int)(SingletonMonoBehaviour<CraftManager>.Instance.CraftNum - 1);
		CraftNumDD.RefreshShownValue();
		if (MaxCraftNum == 1)
		{
			CraftNumDD.interactable = false;
		}
		else
		{
			CraftNumDD.interactable = true;
		}
		Icon.Load(RecipeDetail.ProductItem.IconName, RecipeDetail.ProductItem.IconColorId);
		ItemNameText.text = RecipeDetail.ProductItem.Name;
		CostText.text = RecipeDetail.Const.ToString();
		TimeSpan timeSpan = new TimeSpan(0, 0, (int)RecipeDetail.TimeSeconds);
		TimeText.text = timeSpan.ToString();
		TableView.LoadData(RecipeDetail);
		if (SingletonMonoBehaviour<NavigationViewController>.Instance.PrevNavigationDir == NavigationViewController.NavigationDir.Forward)
		{
			StartCoroutine(AutoMaterial());
		}
	}

	public void OnValueChangedCraftNum(int ddIndex)
	{
		SingletonMonoBehaviour<CraftManager>.Instance.CraftNum = (uint)(ddIndex + 1);
		StartCoroutine(AutoMaterial());
	}

	public void CreateItem()
	{
		bool flag = false;
		if (!SingletonMonoBehaviour<ProfileManager>.Instance.CanCraft())
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "本編でクラフトを解放していないため利用できません。\n解放後再ログインしてお試しください。");
		}
		else if (SingletonMonoBehaviour<CraftManager>.Instance.IsFillMaterial() || flag)
		{
			SingletonMonoBehaviour<NavigationViewController>.Instance.Push(MakingPage);
		}
		else
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "作成に必要な素材が選択されていません");
		}
	}

	public IEnumerator AutoMaterial()
	{
		SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		SingletonMonoBehaviour<CraftManager>.Instance.ClearMaterials();
		foreach (CraftRecipeMaterial mat in RecipeDetail.Materials)
		{
			yield return ItemStorage.GetItemFromAllAvailableStorageForCraft(delegate(CharacterItemStorageList res)
			{
				SingletonMonoBehaviour<CraftManager>.Instance.SetMaterialAuto(res, mat.Num * SingletonMonoBehaviour<CraftManager>.Instance.CraftNum);
				TableView.RefreshSelectedNum();
			}, null, mat.Item.ItemID, CacheOption.OneMinute, LoadingAnimation.Default);
			yield return new WaitForSeconds(0.3f);
		}
		SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
	}
}
