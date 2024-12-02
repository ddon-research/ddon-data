using System;
using System.Collections;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.Networking;

namespace WebRequest;

public class ItemStorage
{
	private static Dictionary<string, CacheValue<StorageSlotNum>> Cache_GetBagUseSlotNum = new Dictionary<string, CacheValue<StorageSlotNum>>();

	private static Dictionary<string, CacheValue<StorageSlotNum>> Cache_GetBagMaterialSlotNum = new Dictionary<string, CacheValue<StorageSlotNum>>();

	private static Dictionary<string, CacheValue<StorageSlotNum>> Cache_GetBagEquipSlotNum = new Dictionary<string, CacheValue<StorageSlotNum>>();

	private static Dictionary<string, CacheValue<StorageSlotNum>> Cache_GetBagJobSlotNum = new Dictionary<string, CacheValue<StorageSlotNum>>();

	private static Dictionary<string, CacheValue<CharacterItemStorage>> Cache_GetBagUse = new Dictionary<string, CacheValue<CharacterItemStorage>>();

	private static Dictionary<string, CacheValue<CharacterItemStorage>> Cache_GetBagEquip = new Dictionary<string, CacheValue<CharacterItemStorage>>();

	private static Dictionary<string, CacheValue<CharacterItemStorage>> Cache_GetBagMaterial = new Dictionary<string, CacheValue<CharacterItemStorage>>();

	private static Dictionary<string, CacheValue<CharacterItemStorage>> Cache_GetBagJob = new Dictionary<string, CacheValue<CharacterItemStorage>>();

	private static Dictionary<string, CacheValue<StorageSlotNum>> Cache_GetWarehouseFreeSlotNum = new Dictionary<string, CacheValue<StorageSlotNum>>();

	private static Dictionary<string, CacheValue<StorageSlotNum>> Cache_GetWarehouseExSlotNum = new Dictionary<string, CacheValue<StorageSlotNum>>();

	private static Dictionary<string, CacheValue<StorageSlotNum>> Cache_GetBaggageEx1SlotNum = new Dictionary<string, CacheValue<StorageSlotNum>>();

	private static Dictionary<string, CacheValue<StorageSlotNum>> Cache_GetBaggageEx2SlotNum = new Dictionary<string, CacheValue<StorageSlotNum>>();

	private static Dictionary<string, CacheValue<StorageSlotNum>> Cache_GetBaggageEx3SlotNum = new Dictionary<string, CacheValue<StorageSlotNum>>();

	private static Dictionary<string, CacheValue<StorageSlotNum>> Cache_GetDeliveryBoxSlotNum = new Dictionary<string, CacheValue<StorageSlotNum>>();

	private static Dictionary<string, CacheValue<StorageSlotNumList>> Cache_GetStorageSlotNum = new Dictionary<string, CacheValue<StorageSlotNumList>>();

	private static Dictionary<string, CacheValue<CharacterItemStorage>> Cache_GetWarehouseFreeUInt32UInt32 = new Dictionary<string, CacheValue<CharacterItemStorage>>();

	private static Dictionary<string, CacheValue<CharacterItemStorage>> Cache_GetWarehouseExUInt32UInt32 = new Dictionary<string, CacheValue<CharacterItemStorage>>();

	private static Dictionary<string, CacheValue<CharacterItemStorage>> Cache_GetBaggageEx1UInt32UInt32 = new Dictionary<string, CacheValue<CharacterItemStorage>>();

	private static Dictionary<string, CacheValue<CharacterItemStorage>> Cache_GetBaggageEx2UInt32UInt32 = new Dictionary<string, CacheValue<CharacterItemStorage>>();

	private static Dictionary<string, CacheValue<CharacterItemStorage>> Cache_GetBaggageEx3UInt32UInt32 = new Dictionary<string, CacheValue<CharacterItemStorage>>();

	private static Dictionary<string, CacheValue<CharacterItemStorage>> Cache_GetDeliveryBoxUInt32UInt32 = new Dictionary<string, CacheValue<CharacterItemStorage>>();

	private static Dictionary<string, CacheValue<StorageInfoList>> Cache_GetStorageInfo = new Dictionary<string, CacheValue<StorageInfoList>>();

	private static Dictionary<string, CacheValue<CharacterItemStorage>> Cache_GetItemFromStorageStorageTypeUInt32 = new Dictionary<string, CacheValue<CharacterItemStorage>>();

	private static Dictionary<string, CacheValue<CharacterItemStorage>> Cache_GetItemFromStorageForWriteStorageTypeUInt32 = new Dictionary<string, CacheValue<CharacterItemStorage>>();

	private static Dictionary<string, CacheValue<CharacterItemStorageList>> Cache_GetItemFromAllAvailableStorageForCraftUInt32 = new Dictionary<string, CacheValue<CharacterItemStorageList>>();

	public static IEnumerator GetBagUseSlotNum(Action<StorageSlotNum> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/";
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetBagUseSlotNum.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/item_storage/bag_use_slot_num");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			StorageSlotNum storageSlotNum = JsonUtility.FromJson<StorageSlotNum>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<StorageSlotNum> cacheValue = new CacheValue<StorageSlotNum>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = storageSlotNum;
				Cache_GetBagUseSlotNum[cacheKey] = cacheValue;
			}
			onResult(storageSlotNum);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/bag_use_slot_num");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetBagUseSlotNum()
	{
		Cache_GetBagUseSlotNum.Clear();
	}

	public static IEnumerator GetBagMaterialSlotNum(Action<StorageSlotNum> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/";
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetBagMaterialSlotNum.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/item_storage/bag_material_slot_num");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			StorageSlotNum storageSlotNum = JsonUtility.FromJson<StorageSlotNum>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<StorageSlotNum> cacheValue = new CacheValue<StorageSlotNum>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = storageSlotNum;
				Cache_GetBagMaterialSlotNum[cacheKey] = cacheValue;
			}
			onResult(storageSlotNum);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/bag_material_slot_num");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetBagMaterialSlotNum()
	{
		Cache_GetBagMaterialSlotNum.Clear();
	}

	public static IEnumerator GetBagEquipSlotNum(Action<StorageSlotNum> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/";
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetBagEquipSlotNum.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/item_storage/bag_equip_slot_num");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			StorageSlotNum storageSlotNum = JsonUtility.FromJson<StorageSlotNum>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<StorageSlotNum> cacheValue = new CacheValue<StorageSlotNum>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = storageSlotNum;
				Cache_GetBagEquipSlotNum[cacheKey] = cacheValue;
			}
			onResult(storageSlotNum);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/bag_equip_slot_num");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetBagEquipSlotNum()
	{
		Cache_GetBagEquipSlotNum.Clear();
	}

	public static IEnumerator GetBagJobSlotNum(Action<StorageSlotNum> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/";
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetBagJobSlotNum.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/item_storage/bag_job_slot_num");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			StorageSlotNum storageSlotNum = JsonUtility.FromJson<StorageSlotNum>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<StorageSlotNum> cacheValue = new CacheValue<StorageSlotNum>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = storageSlotNum;
				Cache_GetBagJobSlotNum[cacheKey] = cacheValue;
			}
			onResult(storageSlotNum);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/bag_job_slot_num");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetBagJobSlotNum()
	{
		Cache_GetBagJobSlotNum.Clear();
	}

	public static IEnumerator GetBagUse(Action<CharacterItemStorage> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/";
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetBagUse.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/item_storage/bag_use");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterItemStorage characterItemStorage = JsonUtility.FromJson<CharacterItemStorage>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CharacterItemStorage> cacheValue = new CacheValue<CharacterItemStorage>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = characterItemStorage;
				Cache_GetBagUse[cacheKey] = cacheValue;
			}
			onResult(characterItemStorage);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/bag_use");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetBagUse()
	{
		Cache_GetBagUse.Clear();
	}

	public static IEnumerator GetBagEquip(Action<CharacterItemStorage> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/";
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetBagEquip.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/item_storage/bag_equip");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterItemStorage characterItemStorage = JsonUtility.FromJson<CharacterItemStorage>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CharacterItemStorage> cacheValue = new CacheValue<CharacterItemStorage>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = characterItemStorage;
				Cache_GetBagEquip[cacheKey] = cacheValue;
			}
			onResult(characterItemStorage);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/bag_equip");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetBagEquip()
	{
		Cache_GetBagEquip.Clear();
	}

	public static IEnumerator GetBagMaterial(Action<CharacterItemStorage> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/";
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetBagMaterial.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/item_storage/bag_material");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterItemStorage characterItemStorage = JsonUtility.FromJson<CharacterItemStorage>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CharacterItemStorage> cacheValue = new CacheValue<CharacterItemStorage>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = characterItemStorage;
				Cache_GetBagMaterial[cacheKey] = cacheValue;
			}
			onResult(characterItemStorage);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/bag_material");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetBagMaterial()
	{
		Cache_GetBagMaterial.Clear();
	}

	public static IEnumerator GetBagJob(Action<CharacterItemStorage> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/";
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetBagJob.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/item_storage/bag_job");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterItemStorage characterItemStorage = JsonUtility.FromJson<CharacterItemStorage>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CharacterItemStorage> cacheValue = new CacheValue<CharacterItemStorage>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = characterItemStorage;
				Cache_GetBagJob[cacheKey] = cacheValue;
			}
			onResult(characterItemStorage);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/bag_job");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetBagJob()
	{
		Cache_GetBagJob.Clear();
	}

	public static IEnumerator GetWarehouseFreeSlotNum(Action<StorageSlotNum> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/";
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetWarehouseFreeSlotNum.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/item_storage/warehouse_free_slot_num");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			StorageSlotNum storageSlotNum = JsonUtility.FromJson<StorageSlotNum>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<StorageSlotNum> cacheValue = new CacheValue<StorageSlotNum>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = storageSlotNum;
				Cache_GetWarehouseFreeSlotNum[cacheKey] = cacheValue;
			}
			onResult(storageSlotNum);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/warehouse_free_slot_num");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetWarehouseFreeSlotNum()
	{
		Cache_GetWarehouseFreeSlotNum.Clear();
	}

	public static IEnumerator GetWarehouseExSlotNum(Action<StorageSlotNum> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/";
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetWarehouseExSlotNum.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/item_storage/warehouse_ex_slot_num");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			StorageSlotNum storageSlotNum = JsonUtility.FromJson<StorageSlotNum>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<StorageSlotNum> cacheValue = new CacheValue<StorageSlotNum>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = storageSlotNum;
				Cache_GetWarehouseExSlotNum[cacheKey] = cacheValue;
			}
			onResult(storageSlotNum);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/warehouse_ex_slot_num");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetWarehouseExSlotNum()
	{
		Cache_GetWarehouseExSlotNum.Clear();
	}

	public static IEnumerator GetBaggageEx1SlotNum(Action<StorageSlotNum> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/";
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetBaggageEx1SlotNum.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/item_storage/baggage_ex1_slot_num");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			StorageSlotNum storageSlotNum = JsonUtility.FromJson<StorageSlotNum>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<StorageSlotNum> cacheValue = new CacheValue<StorageSlotNum>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = storageSlotNum;
				Cache_GetBaggageEx1SlotNum[cacheKey] = cacheValue;
			}
			onResult(storageSlotNum);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/baggage_ex1_slot_num");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetBaggageEx1SlotNum()
	{
		Cache_GetBaggageEx1SlotNum.Clear();
	}

	public static IEnumerator GetBaggageEx2SlotNum(Action<StorageSlotNum> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/";
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetBaggageEx2SlotNum.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/item_storage/baggage_ex2_slot_num");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			StorageSlotNum storageSlotNum = JsonUtility.FromJson<StorageSlotNum>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<StorageSlotNum> cacheValue = new CacheValue<StorageSlotNum>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = storageSlotNum;
				Cache_GetBaggageEx2SlotNum[cacheKey] = cacheValue;
			}
			onResult(storageSlotNum);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/baggage_ex2_slot_num");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetBaggageEx2SlotNum()
	{
		Cache_GetBaggageEx2SlotNum.Clear();
	}

	public static IEnumerator GetBaggageEx3SlotNum(Action<StorageSlotNum> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/";
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetBaggageEx3SlotNum.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/item_storage/baggage_ex3_slot_num");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			StorageSlotNum storageSlotNum = JsonUtility.FromJson<StorageSlotNum>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<StorageSlotNum> cacheValue = new CacheValue<StorageSlotNum>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = storageSlotNum;
				Cache_GetBaggageEx3SlotNum[cacheKey] = cacheValue;
			}
			onResult(storageSlotNum);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/baggage_ex3_slot_num");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetBaggageEx3SlotNum()
	{
		Cache_GetBaggageEx3SlotNum.Clear();
	}

	public static IEnumerator GetDeliveryBoxSlotNum(Action<StorageSlotNum> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/";
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetDeliveryBoxSlotNum.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/item_storage/delivery_box_slot_num");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			StorageSlotNum storageSlotNum = JsonUtility.FromJson<StorageSlotNum>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<StorageSlotNum> cacheValue = new CacheValue<StorageSlotNum>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = storageSlotNum;
				Cache_GetDeliveryBoxSlotNum[cacheKey] = cacheValue;
			}
			onResult(storageSlotNum);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/delivery_box_slot_num");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetDeliveryBoxSlotNum()
	{
		Cache_GetDeliveryBoxSlotNum.Clear();
	}

	public static IEnumerator GetStorageSlotNum(Action<StorageSlotNumList> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/";
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetStorageSlotNum.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/item_storage/storage_slot_num");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			StorageSlotNumList storageSlotNumList = JsonUtility.FromJson<StorageSlotNumList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<StorageSlotNumList> cacheValue = new CacheValue<StorageSlotNumList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = storageSlotNumList;
				Cache_GetStorageSlotNum[cacheKey] = cacheValue;
			}
			onResult(storageSlotNumList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/storage_slot_num");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetStorageSlotNum()
	{
		Cache_GetStorageSlotNum.Clear();
	}

	public static IEnumerator GetWarehouseFree(Action<CharacterItemStorage> onResult, Action<UnityWebRequest> onError, uint slotMin, uint slotNum, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + slotMin + "/" + slotNum;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetWarehouseFreeUInt32UInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/item_storage/warehouse_free/{slotMin}/{slotNum}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterItemStorage characterItemStorage = JsonUtility.FromJson<CharacterItemStorage>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CharacterItemStorage> cacheValue = new CacheValue<CharacterItemStorage>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = characterItemStorage;
				Cache_GetWarehouseFreeUInt32UInt32[cacheKey] = cacheValue;
			}
			onResult(characterItemStorage);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/warehouse_free/{slotMin}/{slotNum}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetWarehouseFreeUInt32UInt32()
	{
		Cache_GetWarehouseFreeUInt32UInt32.Clear();
	}

	public static IEnumerator GetWarehouseEx(Action<CharacterItemStorage> onResult, Action<UnityWebRequest> onError, uint slotMin, uint slotNum, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + slotMin + "/" + slotNum;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetWarehouseExUInt32UInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/item_storage/warehouse_ex/{slotMin}/{slotNum}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterItemStorage characterItemStorage = JsonUtility.FromJson<CharacterItemStorage>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CharacterItemStorage> cacheValue = new CacheValue<CharacterItemStorage>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = characterItemStorage;
				Cache_GetWarehouseExUInt32UInt32[cacheKey] = cacheValue;
			}
			onResult(characterItemStorage);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/warehouse_ex/{slotMin}/{slotNum}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetWarehouseExUInt32UInt32()
	{
		Cache_GetWarehouseExUInt32UInt32.Clear();
	}

	public static IEnumerator GetBaggageEx1(Action<CharacterItemStorage> onResult, Action<UnityWebRequest> onError, uint slotMin, uint slotNum, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + slotMin + "/" + slotNum;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetBaggageEx1UInt32UInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/item_storage/baggage_ex1/{slotMin}/{slotNum}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterItemStorage characterItemStorage = JsonUtility.FromJson<CharacterItemStorage>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CharacterItemStorage> cacheValue = new CacheValue<CharacterItemStorage>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = characterItemStorage;
				Cache_GetBaggageEx1UInt32UInt32[cacheKey] = cacheValue;
			}
			onResult(characterItemStorage);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/baggage_ex1/{slotMin}/{slotNum}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetBaggageEx1UInt32UInt32()
	{
		Cache_GetBaggageEx1UInt32UInt32.Clear();
	}

	public static IEnumerator GetBaggageEx2(Action<CharacterItemStorage> onResult, Action<UnityWebRequest> onError, uint slotMin, uint slotNum, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + slotMin + "/" + slotNum;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetBaggageEx2UInt32UInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/item_storage/baggage_ex2/{slotMin}/{slotNum}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterItemStorage characterItemStorage = JsonUtility.FromJson<CharacterItemStorage>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CharacterItemStorage> cacheValue = new CacheValue<CharacterItemStorage>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = characterItemStorage;
				Cache_GetBaggageEx2UInt32UInt32[cacheKey] = cacheValue;
			}
			onResult(characterItemStorage);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/baggage_ex2/{slotMin}/{slotNum}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetBaggageEx2UInt32UInt32()
	{
		Cache_GetBaggageEx2UInt32UInt32.Clear();
	}

	public static IEnumerator GetBaggageEx3(Action<CharacterItemStorage> onResult, Action<UnityWebRequest> onError, uint slotMin, uint slotNum, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + slotMin + "/" + slotNum;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetBaggageEx3UInt32UInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/item_storage/baggage_ex3/{slotMin}/{slotNum}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterItemStorage characterItemStorage = JsonUtility.FromJson<CharacterItemStorage>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CharacterItemStorage> cacheValue = new CacheValue<CharacterItemStorage>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = characterItemStorage;
				Cache_GetBaggageEx3UInt32UInt32[cacheKey] = cacheValue;
			}
			onResult(characterItemStorage);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/baggage_ex3/{slotMin}/{slotNum}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetBaggageEx3UInt32UInt32()
	{
		Cache_GetBaggageEx3UInt32UInt32.Clear();
	}

	public static IEnumerator GetDeliveryBox(Action<CharacterItemStorage> onResult, Action<UnityWebRequest> onError, uint slotMin, uint slotNum, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + slotMin + "/" + slotNum;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetDeliveryBoxUInt32UInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/item_storage/delivery_box/{slotMin}/{slotNum}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterItemStorage characterItemStorage = JsonUtility.FromJson<CharacterItemStorage>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CharacterItemStorage> cacheValue = new CacheValue<CharacterItemStorage>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = characterItemStorage;
				Cache_GetDeliveryBoxUInt32UInt32[cacheKey] = cacheValue;
			}
			onResult(characterItemStorage);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/delivery_box/{slotMin}/{slotNum}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetDeliveryBoxUInt32UInt32()
	{
		Cache_GetDeliveryBoxUInt32UInt32.Clear();
	}

	public static IEnumerator GetStorageInfo(Action<StorageInfoList> onResult, Action<UnityWebRequest> onError, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/";
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetStorageInfo.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + "/api/item_storage/storage_info");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			StorageInfoList storageInfoList = JsonUtility.FromJson<StorageInfoList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<StorageInfoList> cacheValue = new CacheValue<StorageInfoList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = storageInfoList;
				Cache_GetStorageInfo[cacheKey] = cacheValue;
			}
			onResult(storageInfoList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/storage_info");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetStorageInfo()
	{
		Cache_GetStorageInfo.Clear();
	}

	public static IEnumerator GetItemFromStorage(Action<CharacterItemStorage> onResult, Action<UnityWebRequest> onError, StorageType storageType, uint itemId, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = string.Concat("/", storageType, "/", itemId);
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetItemFromStorageStorageTypeUInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/item_storage/item_from_storage_r/{storageType}/{itemId}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterItemStorage characterItemStorage = JsonUtility.FromJson<CharacterItemStorage>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CharacterItemStorage> cacheValue = new CacheValue<CharacterItemStorage>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = characterItemStorage;
				Cache_GetItemFromStorageStorageTypeUInt32[cacheKey] = cacheValue;
			}
			onResult(characterItemStorage);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/item_from_storage_r/{storageType}/{itemId}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetItemFromStorageStorageTypeUInt32()
	{
		Cache_GetItemFromStorageStorageTypeUInt32.Clear();
	}

	public static IEnumerator GetItemFromStorageForWrite(Action<CharacterItemStorage> onResult, Action<UnityWebRequest> onError, StorageType storageType, uint itemId, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = string.Concat("/", storageType, "/", itemId);
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetItemFromStorageForWriteStorageTypeUInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/item_storage/item_from_storage_w/{storageType}/{itemId}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterItemStorage characterItemStorage = JsonUtility.FromJson<CharacterItemStorage>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CharacterItemStorage> cacheValue = new CacheValue<CharacterItemStorage>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = characterItemStorage;
				Cache_GetItemFromStorageForWriteStorageTypeUInt32[cacheKey] = cacheValue;
			}
			onResult(characterItemStorage);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/item_from_storage_w/{storageType}/{itemId}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetItemFromStorageForWriteStorageTypeUInt32()
	{
		Cache_GetItemFromStorageForWriteStorageTypeUInt32.Clear();
	}

	public static IEnumerator GetItemFromAllAvailableStorageForCraft(Action<CharacterItemStorageList> onResult, Action<UnityWebRequest> onError, uint itemId, CacheOption cacheOption = null, LoadingAnimation loadAnim = LoadingAnimation.None)
	{
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		}
		string cacheKey = "/" + itemId;
		if (cacheOption == null)
		{
			cacheOption = CacheOption.Default;
		}
		if (!cacheOption.IgnoreCache && Cache_GetItemFromAllAvailableStorageForCraftUInt32.TryGetValue(cacheKey, out var value) && value.Expire > DateTime.Now)
		{
			onResult(value.Data);
			if (loadAnim == LoadingAnimation.Default)
			{
				SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			}
			yield break;
		}
		UnityWebRequest request = UnityWebRequest.Get(WebAPIController.Instance.Host + $"/api/item_storage/item_from_ava_claft/{itemId}");
		request.SetRequestHeader("Authorization", WebAPIController.Instance.ApiToken);
		yield return request.Send();
		if (request.responseCode == 200)
		{
			string text = request.downloadHandler.text;
			CharacterItemStorageList characterItemStorageList = JsonUtility.FromJson<CharacterItemStorageList>(text);
			if (!cacheOption.NoCache)
			{
				CacheValue<CharacterItemStorageList> cacheValue = new CacheValue<CharacterItemStorageList>();
				cacheValue.Expire += cacheOption.Expire;
				cacheValue.Data = characterItemStorageList;
				Cache_GetItemFromAllAvailableStorageForCraftUInt32[cacheKey] = cacheValue;
			}
			onResult(characterItemStorageList);
		}
		else
		{
			WebAPIController.Instance.HandleError(request, onError, "api/item_storage/item_from_ava_claft/{itemId}");
		}
		if (loadAnim == LoadingAnimation.Default)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
		}
	}

	public static void ClearCache_GetItemFromAllAvailableStorageForCraftUInt32()
	{
		Cache_GetItemFromAllAvailableStorageForCraftUInt32.Clear();
	}

	public static void ClearCache()
	{
		Cache_GetBagUseSlotNum.Clear();
		Cache_GetBagMaterialSlotNum.Clear();
		Cache_GetBagEquipSlotNum.Clear();
		Cache_GetBagJobSlotNum.Clear();
		Cache_GetBagUse.Clear();
		Cache_GetBagEquip.Clear();
		Cache_GetBagMaterial.Clear();
		Cache_GetBagJob.Clear();
		Cache_GetWarehouseFreeSlotNum.Clear();
		Cache_GetWarehouseExSlotNum.Clear();
		Cache_GetBaggageEx1SlotNum.Clear();
		Cache_GetBaggageEx2SlotNum.Clear();
		Cache_GetBaggageEx3SlotNum.Clear();
		Cache_GetDeliveryBoxSlotNum.Clear();
		Cache_GetStorageSlotNum.Clear();
		Cache_GetWarehouseFreeUInt32UInt32.Clear();
		Cache_GetWarehouseExUInt32UInt32.Clear();
		Cache_GetBaggageEx1UInt32UInt32.Clear();
		Cache_GetBaggageEx2UInt32UInt32.Clear();
		Cache_GetBaggageEx3UInt32UInt32.Clear();
		Cache_GetDeliveryBoxUInt32UInt32.Clear();
		Cache_GetStorageInfo.Clear();
		Cache_GetItemFromStorageStorageTypeUInt32.Clear();
		Cache_GetItemFromStorageForWriteStorageTypeUInt32.Clear();
		Cache_GetItemFromAllAvailableStorageForCraftUInt32.Clear();
	}
}
