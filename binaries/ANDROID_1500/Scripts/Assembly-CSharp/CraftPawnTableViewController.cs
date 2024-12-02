using System.Collections;
using Packet;
using UnityEngine;
using WebRequest;

public class CraftPawnTableViewController : TableViewController<CraftpawnData>
{
	private CraftPawnSelectController.SelectType LoadType = CraftPawnSelectController.SelectType.None;

	public IEnumerator LoadData(CraftPawnSelectController.SelectType type = CraftPawnSelectController.SelectType.MainPawn)
	{
		if (LoadType != type)
		{
			LoadType = type;
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
			TableData.Clear();
			if (LoadType == CraftPawnSelectController.SelectType.MainPawn)
			{
				yield return GetMainPawn();
			}
			else if (LoadType == CraftPawnSelectController.SelectType.SupportPawn)
			{
				yield return GetSupportPawn();
			}
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	private IEnumerator GetMainPawn()
	{
		yield return Craft.GetPawn(delegate(CraftPawnList ret)
		{
			foreach (CraftPawn craftPawn in ret.CraftPawns)
			{
				CraftpawnData craftpawnData = new CraftpawnData
				{
					MyPawnID = craftPawn.MyPawnID,
					PawnName = craftPawn.Name,
					CanCraft = craftPawn.CanCraft,
					RemainTime = craftPawn.RemainTime,
					IsMyPawn = true,
					CraftLv = craftPawn.CraftRank,
					NowExp = craftPawn.NowExp,
					NextExp = craftPawn.NaxtExp
				};
				foreach (CraftSkillLevel skillLevel in craftPawn.SkillLevelList)
				{
					craftpawnData.SkillLvs.Add(skillLevel.CraftType, skillLevel.Level);
				}
				TableData.Add(craftpawnData);
			}
			UpdateContents();
		}, null, CacheOption.OneMinute);
	}

	private IEnumerator GetSupportPawn()
	{
		yield return Craft.GetSupportPawn(delegate(CraftPawnList ret)
		{
			foreach (CraftPawn craftPawn in ret.CraftPawns)
			{
				CraftpawnData craftpawnData = new CraftpawnData
				{
					MyPawnID = craftPawn.MyPawnID,
					PawnName = craftPawn.Name,
					CanCraft = craftPawn.CanCraft,
					RemainTime = craftPawn.RemainTime,
					CraftLv = craftPawn.CraftRank,
					Limit = craftPawn.CraftCount,
					IsMyPawn = false
				};
				foreach (CraftSkillLevel skillLevel in craftPawn.SkillLevelList)
				{
					craftpawnData.SkillLvs.Add(skillLevel.CraftType, skillLevel.Level);
				}
				TableData.Add(craftpawnData);
			}
			UpdateContents();
		}, null, CacheOption.OneMinute);
	}

	private void OnEnable()
	{
		base.CachedScrollRect.content.anchoredPosition = Vector2.zero;
		StartCoroutine(LoadData());
	}
}
