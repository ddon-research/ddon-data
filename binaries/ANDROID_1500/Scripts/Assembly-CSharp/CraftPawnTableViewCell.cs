using DDOAppMaster.Enum.Craft;
using UnityEngine;
using UnityEngine.UI;

public class CraftPawnTableViewCell : TableViewCell<CraftpawnData>
{
	[SerializeField]
	private Text Name;

	[SerializeField]
	private Text NowExp;

	[SerializeField]
	private Text NextExp;

	[SerializeField]
	private Text Limit;

	[SerializeField]
	private Text Lv;

	[SerializeField]
	private Image CanCraft;

	[SerializeField]
	private Image CraftingImg;

	[SerializeField]
	private Image DoneImg;

	[SerializeField]
	private Image DontImage;

	[SerializeField]
	private Text Perf_Speed;

	[SerializeField]
	private Text Perf_GradeUp;

	[SerializeField]
	private Text Perf_Cost;

	[SerializeField]
	private Text Perf_Quality;

	[SerializeField]
	private Text Perf_Num;

	private CraftpawnData Data;

	[SerializeField]
	private CraftPawnSelectController SelectController;

	private CraftPawnSelectController.SelectType SelectType;

	public override void UpdateContent(CraftpawnData pawn)
	{
		Name.text = pawn.PawnName;
		if ((pawn.NowExp != 0 && pawn.NowExp == pawn.NextExp) || !pawn.IsMyPawn)
		{
			NowExp.text = "--";
			NextExp.text = "--";
		}
		else
		{
			NowExp.text = pawn.NowExp.ToString();
			NextExp.text = pawn.NextExp.ToString();
		}
		Limit.text = ((!pawn.IsMyPawn) ? pawn.Limit.ToString() : "∞");
		Lv.text = pawn.CraftLv.ToString();
		if (pawn.CanCraft)
		{
			CanCraft.gameObject.SetActive(value: true);
			DontImage.gameObject.SetActive(value: false);
			CraftingImg.gameObject.SetActive(value: false);
			DoneImg.gameObject.SetActive(value: false);
		}
		else
		{
			CanCraft.gameObject.SetActive(value: false);
			if (!pawn.IsMyPawn && pawn.Limit == 0)
			{
				DontImage.gameObject.SetActive(value: true);
				CraftingImg.gameObject.SetActive(value: false);
				DoneImg.gameObject.SetActive(value: false);
			}
			else
			{
				DontImage.gameObject.SetActive(value: false);
				if (pawn.RemainTime > 0)
				{
					CraftingImg.gameObject.SetActive(value: true);
					DoneImg.gameObject.SetActive(value: false);
				}
				else
				{
					CraftingImg.gameObject.SetActive(value: false);
					DoneImg.gameObject.SetActive(value: true);
				}
			}
		}
		CanCraft.gameObject.SetActive(pawn.CanCraft);
		Perf_Speed.text = GetSkillLvText(pawn, CraftSkillType.PAWN_CRAFT_SKILL_SPEEDUP);
		Perf_GradeUp.text = GetSkillLvText(pawn, CraftSkillType.PAWN_CRAFT_SKILL_GRADEUP);
		Perf_Cost.text = GetSkillLvText(pawn, CraftSkillType.PAWN_CRAFT_SKILL_COSTDOWN);
		Perf_Quality.text = GetSkillLvText(pawn, CraftSkillType.PAWN_CRAFT_SKILL_QUALITYUP);
		Perf_Num.text = GetSkillLvText(pawn, CraftSkillType.PAWN_CRAFT_SKILL_ITEMNUM);
		Data = pawn;
	}

	private string GetSkillLvText(CraftpawnData pawn, CraftSkillType type)
	{
		if (pawn.SkillLvs.ContainsKey(type))
		{
			return (pawn.SkillLvs[type] + 1).ToString();
		}
		return "1";
	}

	public void DecidePawn()
	{
		if (!Data.IsMyPawn && Data.Limit == 0)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "残りクラフト回数が0の為選択できません");
		}
		else if (!Data.CanCraft)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "現在クラフト中の為選択できません");
		}
		else
		{
			SelectController.DeicePawn(Data);
		}
	}
}
