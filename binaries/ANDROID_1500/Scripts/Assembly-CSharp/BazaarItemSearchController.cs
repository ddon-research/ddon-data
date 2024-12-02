using System;
using System.Collections;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class BazaarItemSearchController : ViewController
{
	public class DDOptionExtend : Dropdown.OptionData
	{
		public uint ID;

		public DDOptionExtend(string t)
		{
			base.text = t;
		}
	}

	public enum ViewMode
	{
		Buy,
		Sell
	}

	[SerializeField]
	private Dropdown MainCategoryDD;

	[SerializeField]
	private Dropdown SubCategoryDD;

	[SerializeField]
	private Dropdown RankDD;

	[SerializeField]
	private InputField RankInput;

	[SerializeField]
	private Text NumResultText;

	[SerializeField]
	private BazaarItemTableViewController TableView;

	[SerializeField]
	private Button SearchButton;

	[SerializeField]
	private GameObject SearchResultNumArea;

	[SerializeField]
	private GameObject TooManyResultCaution;

	[SerializeField]
	private Text EmptyText;

	private uint Rank;

	private ViewMode Mode;

	[SerializeField]
	private Sprite BuyIcon;

	[SerializeField]
	private Sprite SelIcon;

	[SerializeField]
	private BazaarBuyController BuyView;

	[SerializeField]
	private BazaarSellController SellView;

	public override string Title
	{
		get
		{
			if (Mode == ViewMode.Buy)
			{
				return "バザー購入";
			}
			return "バザー出品";
		}
		set
		{
			base.Title = value;
		}
	}

	public override Sprite Icon
	{
		get
		{
			if (Mode == ViewMode.Buy)
			{
				return BuyIcon;
			}
			return SelIcon;
		}
	}

	private void Start()
	{
		MainCategoryDD.onValueChanged.AddListener(OnValueChangedMainCategory);
		SearchButton.onClick.AddListener(Search);
		RankInput.onEndEdit.AddListener(OnEndEditRank);
		RankInput.text = "1";
		MainCategoryDD.options.Add(new DDOptionExtend("未選択"));
		MainCategoryDD.RefreshShownValue();
		StartCoroutine(Bazaar.GetMainCategoryList(delegate(BazaarCategoryList res)
		{
			foreach (BazaarCategory category in res.Categories)
			{
				DDOptionExtend item = new DDOptionExtend(category.Name)
				{
					ID = category.ID
				};
				MainCategoryDD.options.Add(item);
			}
		}, null, CacheOption.OneDay, LoadingAnimation.Default));
	}

	private void OnEnable()
	{
		SingletonMonoBehaviour<TutorialManager>.Instance.StartTutorial(TutorialManager.TutorialType.TUTORIAL_BAZAAR_BUY);
		if (SingletonMonoBehaviour<NavigationViewController>.Instance.PrevNavigationDir == NavigationViewController.NavigationDir.Forward)
		{
			TooManyResultCaution.SetActive(value: false);
			MainCategoryDD.value = 0;
			MainCategoryDD.RefreshShownValue();
			SubCategoryDD.options.Clear();
			SubCategoryDD.value = 0;
			SubCategoryDD.RefreshShownValue();
			TableView.Initialize();
			SearchResultNumArea.SetActive(value: false);
			SearchButton.interactable = false;
		}
		else if (SingletonMonoBehaviour<NavigationViewController>.Instance.PrevNavigationDir != NavigationViewController.NavigationDir.Back)
		{
		}
		if (TableView.IsContents)
		{
			EmptyText.enabled = false;
		}
		else
		{
			EmptyText.enabled = true;
		}
	}

	private void OnValueChangedMainCategory(int index)
	{
		DDOptionExtend dDOptionExtend = MainCategoryDD.options[index] as DDOptionExtend;
		SubCategoryDD.ClearOptions();
		SubCategoryDD.itemText.text = string.Empty;
		if (MainCategoryDD.value > 0)
		{
			StartCoroutine(Bazaar.GetSubCategoryList(delegate(BazaarCategoryList res)
			{
				if (res.Categories.Count == 1)
				{
					DDOptionExtend item = new DDOptionExtend("すべて")
					{
						ID = res.Categories[0].ID
					};
					SubCategoryDD.options.Add(item);
				}
				else
				{
					SubCategoryDD.options.Add(new DDOptionExtend("すべて"));
					foreach (BazaarCategory category in res.Categories)
					{
						DDOptionExtend item2 = new DDOptionExtend(category.Name)
						{
							ID = category.ID
						};
						SubCategoryDD.options.Add(item2);
					}
				}
				SubCategoryDD.value = 0;
				SubCategoryDD.RefreshShownValue();
			}, null, dDOptionExtend.ID, CacheOption.OneDay, LoadingAnimation.Default));
		}
		SearchButton.interactable = MainCategoryDD.value > 0;
	}

	private void OnEndEditRank(string text)
	{
		if (!int.TryParse(text, out var result))
		{
			Rank = 1u;
		}
		if (result < 1)
		{
			result = 1;
		}
		else if (result > 999)
		{
			result = 999;
		}
		Rank = (uint)result;
		RankInput.text = Rank.ToString();
	}

	private void Search()
	{
		DDOptionExtend dDOptionExtend = MainCategoryDD.options[MainCategoryDD.value] as DDOptionExtend;
		DDOptionExtend dDOptionExtend2 = SubCategoryDD.options[SubCategoryDD.value] as DDOptionExtend;
		EmptyText.enabled = false;
		TableView.LoadData(dDOptionExtend.ID, dDOptionExtend2.ID, Rank, delegate(uint num, bool isTooMany)
		{
			SearchResultNumArea.SetActive(value: true);
			NumResultText.text = num.ToString();
			TooManyResultCaution.SetActive(isTooMany);
		});
	}

	public void OnClickElement(BazaarItem itemData)
	{
		if (Mode == ViewMode.Buy)
		{
			BuyView.Setup(itemData);
			BuyView.Push();
		}
		else if (Mode == ViewMode.Sell)
		{
			StartCoroutine(ShowSellView(itemData, delegate(List<StorageSlotItem> storageItems)
			{
				SellView.Initialize(itemData.Item.ItemID, itemData.Item.Name, itemData.Item.IconName, itemData.Item.IconColorId, storageItems);
				SellView.Push();
			}));
		}
	}

	public static IEnumerator ShowSellView(BazaarItem itemData, Action<List<StorageSlotItem>> onShowSellView)
	{
		yield return ItemStorage.GetItemFromAllAvailableStorageForCraft(delegate(CharacterItemStorageList res)
		{
			List<StorageSlotItem> storageItems = new List<StorageSlotItem>();
			uint num = 0u;
			foreach (CharacterItemStorage storage in res.StorageList)
			{
				foreach (StorageItem item2 in storage.ItemList)
				{
					if (item2.Num != 0)
					{
						StorageSlotItem item = new StorageSlotItem
						{
							Address = 
							{
								Storage = storage.StorageType,
								SlotNo = item2.SlotNo
							},
							Item = item2.Item,
							Num = item2.Num
						};
						storageItems.Add(item);
						num += item2.Num;
					}
				}
			}
			if (num == 0)
			{
				SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "指定されたアイテムは所持していません");
			}
			else
			{
				SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "出品可能なアイテムが見つかりました", res.ToString(), delegate
				{
					onShowSellView(storageItems);
				});
			}
		}, null, itemData.Item.ItemID, CacheOption.OneMinute, LoadingAnimation.Default);
	}

	public void PushBuy()
	{
		Mode = ViewMode.Buy;
		Push();
	}

	public void PushSell()
	{
		Mode = ViewMode.Sell;
		Push();
	}
}
