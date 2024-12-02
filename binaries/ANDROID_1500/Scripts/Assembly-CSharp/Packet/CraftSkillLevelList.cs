using System;
using System.Collections.Generic;
using System.Linq;
using DDOAppMaster.Enum.Craft;

namespace Packet;

[Serializable]
public class CraftSkillLevelList
{
	public List<CraftSkillLevel> List = new List<CraftSkillLevel>();

	public static CraftSkillLevelList ConvertCollection(ICollection<CraftSkillLevel> col)
	{
		CraftSkillLevelList ret = new CraftSkillLevelList();
		col.ToList().ForEach(delegate(CraftSkillLevel x)
		{
			ret.List.Add(x);
		});
		return ret;
	}

	public List<CraftSkillLevel> GetCraftSkillByTypeList(CraftSkillType type)
	{
		return List.Where((CraftSkillLevel x) => x.CraftType == type).ToList();
	}

	public List<CraftSkillLevel> GetCraftSkillSpeedUpList()
	{
		return GetCraftSkillByTypeList(CraftSkillType.PAWN_CRAFT_SKILL_SPEEDUP);
	}

	public List<CraftSkillLevel> GetCraftSkillCostCutList()
	{
		return GetCraftSkillByTypeList(CraftSkillType.PAWN_CRAFT_SKILL_COSTDOWN);
	}

	public CraftSkillLevel GetCraftSkillCostCut()
	{
		List<CraftSkillLevel> craftSkillCostCutList = GetCraftSkillCostCutList();
		if (craftSkillCostCutList == null)
		{
			return null;
		}
		if (craftSkillCostCutList.Count <= 0)
		{
			return null;
		}
		return craftSkillCostCutList.First();
	}

	public List<CraftSkillLevel> GetCraftSkillCostCutNoLimitList()
	{
		return GetCraftSkillByTypeList(CraftSkillType.PAWN_CRAFT_SKILL_NO_LIMIT_ASSIST_COSTDOWN);
	}

	public CraftSkillLevel GetCraftSkillCostCutNoLimit()
	{
		List<CraftSkillLevel> craftSkillCostCutNoLimitList = GetCraftSkillCostCutNoLimitList();
		if (craftSkillCostCutNoLimitList == null)
		{
			return null;
		}
		if (craftSkillCostCutNoLimitList.Count <= 0)
		{
			return null;
		}
		return craftSkillCostCutNoLimitList.First();
	}

	public List<CraftSkillLevel> GetCraftSkillUseSpSkillTableList()
	{
		return GetCraftSkillByTypeList(CraftSkillType.PAWN_CRAFT_SKILL_USE_SP_SKILL_TABLE);
	}

	public List<CraftSkillLevel> GetCraftSkillItemNumUpList()
	{
		return GetCraftSkillByTypeList(CraftSkillType.PAWN_CRAFT_SKILL_ITEMNUM);
	}

	public CraftSkillLevel GetCraftSkillItemNumUp()
	{
		List<CraftSkillLevel> craftSkillItemNumUpList = GetCraftSkillItemNumUpList();
		if (craftSkillItemNumUpList == null)
		{
			return null;
		}
		if (craftSkillItemNumUpList.Count <= 0)
		{
			return null;
		}
		return craftSkillItemNumUpList.First();
	}

	public List<CraftSkillLevel> GetCraftSkillPerfectItemNumList()
	{
		return GetCraftSkillByTypeList(CraftSkillType.PAWN_CRAFT_SKILL_PERFECT_ITEMNUM);
	}

	public CraftSkillLevel GetCraftSkillPerfectItemNum()
	{
		List<CraftSkillLevel> craftSkillPerfectItemNumList = GetCraftSkillPerfectItemNumList();
		if (craftSkillPerfectItemNumList == null)
		{
			return null;
		}
		if (craftSkillPerfectItemNumList.Count <= 0)
		{
			return null;
		}
		return craftSkillPerfectItemNumList.First();
	}

	public List<CraftSkillLevel> GetCraftSkillRareItemNumBonusList()
	{
		return GetCraftSkillByTypeList(CraftSkillType.PAWN_CRAFT_SKILL_RARE_ITEMNUM_BONUS);
	}

	public CraftSkillLevel GetCraftSkillRareItemNumBonus()
	{
		List<CraftSkillLevel> craftSkillRareItemNumBonusList = GetCraftSkillRareItemNumBonusList();
		if (craftSkillRareItemNumBonusList == null)
		{
			return null;
		}
		if (craftSkillRareItemNumBonusList.Count <= 0)
		{
			return null;
		}
		return craftSkillRareItemNumBonusList.First();
	}

	public List<CraftSkillLevel> GetCraftSkillQualityUpList()
	{
		return GetCraftSkillByTypeList(CraftSkillType.PAWN_CRAFT_SKILL_QUALITYUP);
	}

	public List<CraftSkillLevel> GetCraftSkillPerfectQualityUpList()
	{
		return GetCraftSkillByTypeList(CraftSkillType.PAWN_CRAFT_SKILL_PERFECT_QUALITYUP);
	}

	public CraftSkillLevel GetCraftSkillPerfectQualityUp()
	{
		List<CraftSkillLevel> craftSkillPerfectQualityUpList = GetCraftSkillPerfectQualityUpList();
		if (craftSkillPerfectQualityUpList == null)
		{
			return null;
		}
		if (craftSkillPerfectQualityUpList.Count <= 0)
		{
			return null;
		}
		return craftSkillPerfectQualityUpList.First();
	}
}
