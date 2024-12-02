using System;
using DDOAppMaster.Enum.Craft;
using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class CraftMakingPage : MonoBehaviour
{
	[SerializeField]
	private Text ItemName;

	[SerializeField]
	private Text LeaderName;

	[SerializeField]
	private Text AssistName1;

	[SerializeField]
	private Text AssistName2;

	[SerializeField]
	private Text AssistName3;

	[SerializeField]
	private Text RefineItemName;

	[SerializeField]
	private Text Perf_SpeedText;

	[SerializeField]
	private Text Perf_GradeUpText;

	[SerializeField]
	private Text Perf_QualityText;

	[SerializeField]
	private Text Perf_CostText;

	[SerializeField]
	private Text SpText;

	[SerializeField]
	private ItemIcon Status_ItemIcon;

	[SerializeField]
	private Text Status_ItemName;

	[SerializeField]
	private Text Status_CreateNum;

	[SerializeField]
	private Text Status_Exp;

	[SerializeField]
	private Text Status_DefaultTime;

	[SerializeField]
	private Text Status_ResultTime;

	[SerializeField]
	private Text Status_DefaultCost;

	[SerializeField]
	private Text Status_ResultCost;

	[SerializeField]
	private Text Status_BeforeGold;

	[SerializeField]
	private Text Status_AfterGold;

	[SerializeField]
	private Text Status_JemPrice;

	[SerializeField]
	private Text Status_BeforeJem;

	[SerializeField]
	private Text Status_AfterJem;

	[SerializeField]
	private GameObject RefineItemArea;

	[SerializeField]
	private Text AppDiscountCostRate;

	[SerializeField]
	private Text AppDiscountSpeedRate;

	[SerializeField]
	private CraftPawnSelectController PawnSelectPage;

	[SerializeField]
	private ViewController AcceptedView;

	private void OnEnable()
	{
		GetComponent<RectTransform>().anchoredPosition = Vector2.zero;
		ItemName.text = string.Empty;
		LeaderName.text = string.Empty;
		AssistName1.text = string.Empty;
		AssistName2.text = string.Empty;
		AssistName3.text = string.Empty;
		RefineItemName.text = string.Empty;
		SpText.gameObject.SetActive(value: false);
		StartCoroutine(Craft.GetAppDiscount(delegate(CraftAppDiscount res)
		{
			AppDiscountCostRate.text = res.CostDiscountRate.ToString();
			AppDiscountSpeedRate.text = res.SppedDiscountRate.ToString();
		}, null, CacheOption.OneHour));
		UpdateContent();
		StartCoroutine(Craft.GetExpRate(delegate(CraftExpRate res)
		{
			if (res.ExpRate != 100)
			{
				CraftManager instance = SingletonMonoBehaviour<CraftManager>.Instance;
				uint craftNum = SingletonMonoBehaviour<CraftManager>.Instance.CraftNum;
				float num = (float)res.ExpRate / 100f;
				uint num2 = (uint)((float)instance.RecipeDetail.Exp * num) * craftNum;
				uint num3 = instance.RecipeDetail.Exp * craftNum;
				Status_Exp.text = num2 + "(+" + (num2 - num3).ToString() + ")";
			}
		}, null, CacheOption.OneMinute));
	}

	public void SelectLeader()
	{
		SelectPawn(CraftPawnSelectController.SelectTargetType.Leader);
	}

	public void SelectAssist1()
	{
		if (SingletonMonoBehaviour<CraftManager>.Instance.Leader == null)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "先にリーダーを選択してください");
		}
		else
		{
			SelectPawn(CraftPawnSelectController.SelectTargetType.Assist1);
		}
	}

	public void SelectAssist2()
	{
		if (SingletonMonoBehaviour<CraftManager>.Instance.Leader == null)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "先にリーダーを選択してください");
		}
		else
		{
			SelectPawn(CraftPawnSelectController.SelectTargetType.Assist2);
		}
	}

	public void SelectAssist3()
	{
		if (SingletonMonoBehaviour<CraftManager>.Instance.Leader == null)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "先にリーダーを選択してください");
		}
		else
		{
			SelectPawn(CraftPawnSelectController.SelectTargetType.Assist3);
		}
	}

	public void SelectPawn(CraftPawnSelectController.SelectTargetType type)
	{
		PawnSelectPage.SelectTarget = type;
		SingletonMonoBehaviour<NavigationViewController>.Instance.Push(PawnSelectPage);
	}

	public void DeleteLeader()
	{
		if (SingletonMonoBehaviour<CraftManager>.Instance.Assist1 != null || SingletonMonoBehaviour<CraftManager>.Instance.Assist2 != null || SingletonMonoBehaviour<CraftManager>.Instance.Assist3 != null)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK_Cancel, "確認", "リーダーの選択を解除した場合は、すべてのメンバー選択が解除されます。\nよろしいですか？", delegate(ModalDialog.Result res)
			{
				if (res == ModalDialog.Result.OK)
				{
					SingletonMonoBehaviour<CraftManager>.Instance.Leader = null;
					LeaderName.text = string.Empty;
					DeleteAssist1();
					DeleteAssist2();
					DeleteAssist3();
				}
			});
		}
		else
		{
			SingletonMonoBehaviour<CraftManager>.Instance.Leader = null;
			LeaderName.text = string.Empty;
		}
		UpdateContent();
	}

	public void DeleteAssist1()
	{
		SingletonMonoBehaviour<CraftManager>.Instance.Assist1 = null;
		AssistName1.text = string.Empty;
		UpdateContent();
	}

	public void DeleteAssist2()
	{
		SingletonMonoBehaviour<CraftManager>.Instance.Assist2 = null;
		AssistName2.text = string.Empty;
		UpdateContent();
	}

	public void DeleteAssist3()
	{
		SingletonMonoBehaviour<CraftManager>.Instance.Assist3 = null;
		AssistName3.text = string.Empty;
		UpdateContent();
	}

	public void DeleteRefineItem()
	{
		SingletonMonoBehaviour<CraftManager>.Instance.RefineItem = null;
		RefineItemName.text = string.Empty;
		UpdateContent();
	}

	public void UpdateContent()
	{
		SpText.gameObject.SetActive(value: false);
		CraftManager instance = SingletonMonoBehaviour<CraftManager>.Instance;
		ItemName.text = instance.RecipeDetail.ProductItem.Name;
		if (instance.Leader != null)
		{
			LeaderName.text = instance.Leader.PawnName;
		}
		if (instance.Assist1 != null)
		{
			AssistName1.text = instance.Assist1.PawnName;
		}
		if (instance.Assist2 != null)
		{
			AssistName2.text = instance.Assist2.PawnName;
		}
		if (instance.Assist3 != null)
		{
			AssistName3.text = instance.Assist3.PawnName;
		}
		if (instance.RefineItem != null)
		{
			RefineItemName.text = instance.RefineItem.Item.Name;
		}
		uint craftNum = SingletonMonoBehaviour<CraftManager>.Instance.CraftNum;
		Perf_SpeedText.text = SingletonMonoBehaviour<CraftManager>.Instance.GetSkillLvStringForDisplay(CraftSkillType.PAWN_CRAFT_SKILL_SPEEDUP);
		Perf_GradeUpText.text = SingletonMonoBehaviour<CraftManager>.Instance.GetSkillLvStringForDisplay(CraftSkillType.PAWN_CRAFT_SKILL_GRADEUP);
		Perf_QualityText.text = SingletonMonoBehaviour<CraftManager>.Instance.GetSkillLvStringForDisplay(CraftSkillType.PAWN_CRAFT_SKILL_QUALITYUP);
		Perf_CostText.text = SingletonMonoBehaviour<CraftManager>.Instance.GetSkillLvStringForDisplay(CraftSkillType.PAWN_CRAFT_SKILL_COSTDOWN);
		Status_ItemIcon.Load(instance.RecipeDetail.ProductItem.IconName, instance.RecipeDetail.ProductItem.IconColorId);
		Status_ItemName.text = instance.RecipeDetail.ProductItem.Name;
		Status_CreateNum.text = (instance.RecipeDetail.ProductNum * craftNum).ToString("N0");
		Status_Exp.text = (instance.RecipeDetail.Exp * craftNum).ToString();
		TimeSpan timeSpan = TimeSpan.FromSeconds(instance.RecipeDetail.TimeSeconds);
		Status_DefaultTime.text = new TimeSpan(timeSpan.Ticks * craftNum).ToString();
		Status_ResultTime.text = Status_DefaultTime.text;
		Status_DefaultCost.text = (instance.RecipeDetail.Const * craftNum).ToString("N0");
		Status_ResultCost.text = Status_DefaultCost.text;
		if (SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData != null)
		{
			Status_BeforeGold.text = SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData.Gold.ToString("N0");
			uint num = SingletonMonoBehaviour<CraftManager>.Instance.RecipeDetail.Const * SingletonMonoBehaviour<CraftManager>.Instance.CraftNum;
			if (SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData.Gold < num)
			{
				Status_AfterGold.text = "不足しています";
			}
			else
			{
				Status_AfterGold.text = (SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData.Gold - num).ToString("N0");
			}
		}
		uint num2 = 1u;
		Status_JemPrice.text = num2.ToString("N0");
		long toralJem = SingletonMonoBehaviour<ChargeManager>.Instance.GetToralJem();
		Status_BeforeJem.text = toralJem.ToString("N0");
		if (toralJem < num2)
		{
			Status_AfterJem.text = "0";
		}
		else
		{
			Status_AfterJem.text = (toralJem - num2).ToString("N0");
		}
		RefineItemArea.SetActive(instance.RecipeDetail.CanUseRefine);
		if (instance.Leader != null || instance.Assist1 != null || instance.Assist2 != null || instance.Assist3 != null)
		{
			Analyze();
		}
	}

	public void Analyze()
	{
		StartCoroutine(SingletonMonoBehaviour<CraftManager>.Instance.Analyze(delegate
		{
			uint craftNum = SingletonMonoBehaviour<CraftManager>.Instance.CraftNum;
			TimeSpan value = new TimeSpan(SingletonMonoBehaviour<CraftManager>.Instance.ResultTime.Ticks * craftNum);
			if (value.TotalSeconds < 30.0)
			{
				value = TimeSpan.FromSeconds(30.0);
			}
			Status_ResultTime.text = new DateTime(0L).Add(value).ToString("HH:mm:ss");
			Status_ResultCost.text = (SingletonMonoBehaviour<CraftManager>.Instance.ResultCost * craftNum).ToString("N0");
			if (SingletonMonoBehaviour<CraftManager>.Instance.ResultQualityUp != 0)
			{
				SpText.text = "大成功率" + SingletonMonoBehaviour<CraftManager>.Instance.ResultQualityUp + "%";
				SpText.gameObject.SetActive(value: true);
			}
			if (SingletonMonoBehaviour<CraftManager>.Instance.ResultItemNumUpProb != 0)
			{
				SpText.text = SingletonMonoBehaviour<CraftManager>.Instance.ResultItemNumUpProb + "%の確率で+" + SingletonMonoBehaviour<CraftManager>.Instance.ResultItemNumUpNum + "個";
				SpText.gameObject.SetActive(value: true);
			}
			if (SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData != null)
			{
				Status_BeforeGold.text = SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData.Gold.ToString("N0");
				if (SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData.Gold < SingletonMonoBehaviour<CraftManager>.Instance.ResultCost * craftNum)
				{
					Status_AfterGold.text = "不足しています";
				}
				else
				{
					Status_AfterGold.text = (SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData.Gold - SingletonMonoBehaviour<CraftManager>.Instance.ResultCost * craftNum).ToString("N0");
				}
			}
		}));
	}

	public void DoCraft()
	{
		SingletonMonoBehaviour<UseJemDialog>.Instance.Show("クラフトを発注", 1u, delegate(bool retBuy)
		{
			if (retBuy)
			{
				SingletonMonoBehaviour<CraftManager>.Instance.DoCraft(delegate(DoCraftResult result)
				{
					SingletonMonoBehaviour<ChargeManager>.Instance.SetJem(result.JemList);
					MainViewController.Instance.SetCharacterGold(result.Gold);
					AcceptedView.PopCount = 4u;
					AcceptedView.Push();
				});
			}
		});
	}
}
