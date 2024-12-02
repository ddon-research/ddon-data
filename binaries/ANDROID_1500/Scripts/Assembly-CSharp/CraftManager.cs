using System;
using System.Collections;
using System.Collections.Generic;
using DDOAppMaster.Enum.Craft;
using Packet;
using WebRequest;

public class CraftManager : SingletonMonoBehaviour<CraftManager>
{
	public CraftMainCategory MainCategory;

	private CraftRecipeDetail _RecipeDetail;

	public uint CraftNum;

	private CraftpawnData _Leader;

	private CraftpawnData _Assist1;

	private CraftpawnData _Assist2;

	private CraftpawnData _Assist3;

	public StorageSlotItem RefineItem;

	public Dictionary<StorageSlot, StorageSlotItem> Materials;

	public Dictionary<CraftSkillType, uint> SkillLvs = new Dictionary<CraftSkillType, uint>();

	public TimeSpan ResultTime;

	public uint ResultCost;

	public uint ResultQualityUp;

	public uint ResultItemNumUpProb;

	public uint ResultItemNumUpNum;

	public uint BeforeGold;

	public uint AfterGold;

	public uint JemPrice;

	public uint BeforeJem;

	public uint AfterJem;

	public CraftRecipeDetail RecipeDetail
	{
		get
		{
			return _RecipeDetail;
		}
		set
		{
			_RecipeDetail = value;
		}
	}

	public CraftpawnData Leader
	{
		get
		{
			return _Leader;
		}
		set
		{
			_Leader = value;
			CalcCraftSkill();
		}
	}

	public CraftpawnData Assist1
	{
		get
		{
			return _Assist1;
		}
		set
		{
			_Assist1 = value;
			CalcCraftSkill();
		}
	}

	public CraftpawnData Assist2
	{
		get
		{
			return _Assist2;
		}
		set
		{
			_Assist2 = value;
			CalcCraftSkill();
		}
	}

	public CraftpawnData Assist3
	{
		get
		{
			return _Assist3;
		}
		set
		{
			_Assist3 = value;
			CalcCraftSkill();
		}
	}

	public void Clear()
	{
		RecipeDetail = null;
		Leader = null;
		Assist1 = null;
		Assist2 = null;
		Assist3 = null;
		RefineItem = null;
		Materials = new Dictionary<StorageSlot, StorageSlotItem>();
		CraftNum = 1u;
	}

	private void CalcCraftSkill()
	{
		ClearPerf();
		AddPerf(Leader);
		AddPerf(Assist1);
		AddPerf(Assist2);
		AddPerf(Assist3);
	}

	public uint GetSkillLv(CraftSkillType type)
	{
		if (!SkillLvs.ContainsKey(type))
		{
			return 0u;
		}
		return SkillLvs[type];
	}

	public string GetSkillLvStringForDisplay(CraftSkillType type)
	{
		uint num = GetSkillLv(type);
		if (Leader != null)
		{
			num++;
		}
		if (Assist1 != null)
		{
			num++;
		}
		if (Assist2 != null)
		{
			num++;
		}
		if (Assist3 != null)
		{
			num++;
		}
		return num.ToString();
	}

	private void ClearPerf()
	{
		SkillLvs.Clear();
	}

	private void AddPerf(CraftpawnData pawnData)
	{
		if (pawnData == null)
		{
			return;
		}
		foreach (KeyValuePair<CraftSkillType, uint> skillLv in pawnData.SkillLvs)
		{
			if (SkillLvs.ContainsKey(skillLv.Key))
			{
				SkillLvs[skillLv.Key] += skillLv.Value;
			}
			else
			{
				SkillLvs.Add(skillLv.Key, skillLv.Value);
			}
		}
	}

	public bool IsFillMaterial()
	{
		if (RecipeDetail == null)
		{
			return false;
		}
		foreach (CraftRecipeMaterial material in RecipeDetail.Materials)
		{
			if (GetMaterialNum(material.Item.ItemID) != material.Num * CraftNum)
			{
				return false;
			}
		}
		return true;
	}

	public void SetMaterial(StorageSlotItem ia)
	{
		if (Materials.ContainsKey(ia.Address))
		{
			if (ia.Num != 0)
			{
				Materials[ia.Address] = ia;
			}
			else
			{
				Materials.Remove(ia.Address);
			}
		}
		else if (ia.Num != 0)
		{
			Materials.Add(ia.Address, ia);
		}
	}

	public void SetMaterials(List<StorageSlotItem> ias)
	{
		foreach (StorageSlotItem ia in ias)
		{
			SetMaterial(ia);
		}
	}

	public bool SetMaterialAuto(CharacterItemStorageList list, uint num)
	{
		foreach (CharacterItemStorage storage in list.StorageList)
		{
			foreach (StorageItem item in storage.ItemList)
			{
				StorageSlotItem storageSlotItem = new StorageSlotItem();
				storageSlotItem.Address.Storage = storage.StorageType;
				storageSlotItem.Address.SlotNo = item.SlotNo;
				storageSlotItem.Item = item.Item;
				if (item.Num >= num)
				{
					storageSlotItem.Num = num;
					SetMaterial(storageSlotItem);
					return true;
				}
				storageSlotItem.Num = item.Num;
				num -= item.Num;
				SetMaterial(storageSlotItem);
			}
		}
		return false;
	}

	public void ClearMaterials()
	{
		Materials.Clear();
	}

	public uint GetMaterialNum(StorageType storageType, ushort slotNo)
	{
		StorageSlot storageSlot = new StorageSlot();
		storageSlot.Storage = storageType;
		storageSlot.SlotNo = slotNo;
		StorageSlot key = storageSlot;
		if (Materials.ContainsKey(key))
		{
			return Materials[key].Num;
		}
		return 0u;
	}

	public uint GetMaterialNum(uint itemId)
	{
		uint num = 0u;
		foreach (KeyValuePair<StorageSlot, StorageSlotItem> material in Materials)
		{
			if (material.Value.Item.ItemID == itemId)
			{
				num += material.Value.Num;
			}
		}
		return num;
	}

	public uint GetRefineItemNum(StorageType storageType, ushort slotNo)
	{
		if (RefineItem == null)
		{
			return 0u;
		}
		if (RefineItem.Address.Storage == storageType && RefineItem.Address.SlotNo == slotNo)
		{
			return RefineItem.Num;
		}
		return 0u;
	}

	public IEnumerator Analyze(Action onResult)
	{
		TimeSpan defaultTime = TimeSpan.FromSeconds(RecipeDetail.TimeSeconds);
		uint defaultCost = RecipeDetail.Const;
		CraftAnalyzePacket requestPacket = new CraftAnalyzePacket();
		AddCraftPawnParam(requestPacket.MainPawnInfoList, SingletonMonoBehaviour<CraftManager>.Instance.Leader);
		AddCraftPawnParam(requestPacket.AssistPawnInfoList, SingletonMonoBehaviour<CraftManager>.Instance.Assist1);
		AddCraftPawnParam(requestPacket.AssistPawnInfoList, SingletonMonoBehaviour<CraftManager>.Instance.Assist2);
		AddCraftPawnParam(requestPacket.AssistPawnInfoList, SingletonMonoBehaviour<CraftManager>.Instance.Assist3);
		requestPacket.RecipeId = SingletonMonoBehaviour<CraftManager>.Instance.RecipeDetail.RecipeID;
		ResultTime = default(TimeSpan);
		ResultCost = 0u;
		ResultQualityUp = 0u;
		ResultItemNumUpProb = 0u;
		ResultItemNumUpNum = 0u;
		if (SingletonMonoBehaviour<CraftManager>.Instance.RefineItem != null)
		{
			requestPacket.ToppingItemId = SingletonMonoBehaviour<CraftManager>.Instance.RefineItem.Item.ItemID;
		}
		yield return Craft.PostAnalyzeResult(delegate(CraftAnalyzeResultList res)
		{
			foreach (CraftAnalyzeResult item in res.List)
			{
				double num = (double)item.Value1 / 100.0;
				uint value = item.Value2;
				if (item.CraftType == CraftSkillType.PAWN_CRAFT_SKILL_SPEEDUP)
				{
					ResultTime = new TimeSpan((long)((double)defaultTime.Ticks * num));
				}
				else if (item.CraftType == CraftSkillType.PAWN_CRAFT_SKILL_COSTDOWN)
				{
					ResultCost = (uint)((double)defaultCost * num);
				}
				else if (item.CraftType == CraftSkillType.PAWN_CRAFT_SKILL_QUALITYUP)
				{
					ResultQualityUp = (uint)item.Value1;
				}
				else if (item.CraftType == CraftSkillType.PAWN_CRAFT_SKILL_ITEMNUM)
				{
					ResultItemNumUpProb = (uint)item.Value1;
					ResultItemNumUpNum = value;
				}
			}
			onResult();
		}, null, requestPacket, LoadingAnimation.Default);
	}

	private void AddCraftPawnParam(List<CraftPawnParam> paramList, CraftpawnData pawn)
	{
		if (pawn == null)
		{
			return;
		}
		CraftPawnParam craftPawnParam = new CraftPawnParam();
		craftPawnParam.LevelList = new CraftSkillLevelList();
		foreach (KeyValuePair<CraftSkillType, uint> skillLv in pawn.SkillLvs)
		{
			CraftSkillLevel craftSkillLevel = new CraftSkillLevel();
			craftSkillLevel.CraftType = skillLv.Key;
			craftSkillLevel.Level = skillLv.Value;
			craftPawnParam.LevelList.List.Add(craftSkillLevel);
		}
		paramList.Add(craftPawnParam);
	}

	public void DoCraft(Action<DoCraftResult> onFinish)
	{
		CraftRequest req = new CraftRequest();
		req.RecipeID = RecipeDetail.RecipeID;
		if (Leader == null)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "作成を行うポーンを選択してください");
			return;
		}
		if (SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData != null && SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData.Gold < ResultCost)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "所持ゴールドが不足しています");
			return;
		}
		Action<CraftpawnData> action = delegate(CraftpawnData pawn)
		{
			if (pawn != null)
			{
				if (pawn.IsMyPawn)
				{
					req.AssistMyPawns.Add(pawn.MyPawnID);
				}
				else
				{
					req.AssistRentalPawns.Add(pawn.MyPawnID);
				}
			}
		};
		req.MyPawnID = Leader.MyPawnID;
		action(Assist1);
		action(Assist2);
		action(Assist3);
		req.RefineItem = RefineItem;
		req.DoNum = CraftNum;
		foreach (KeyValuePair<StorageSlot, StorageSlotItem> material in Materials)
		{
			req.MaterialItems.Add(material.Value);
		}
		StartCoroutine(Craft.PostDoCraft(onFinish, null, req, LoadingAnimation.Default));
		ItemStorage.ClearCache();
		Craft.ClearCache_GetPawn();
		Craft.ClearCache_GetSupportPawn();
		Craft.ClearCache_GetPawnStatus();
	}
}
