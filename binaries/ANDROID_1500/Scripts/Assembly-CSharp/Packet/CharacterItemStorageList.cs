using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class CharacterItemStorageList
{
	public List<CharacterItemStorage> StorageList = new List<CharacterItemStorage>();

	public new string ToString()
	{
		string text = string.Empty;
		Func<List<StorageItem>, uint> func = delegate(List<StorageItem> list)
		{
			uint num = 0u;
			foreach (StorageItem item in list)
			{
				num += item.Num;
			}
			return num;
		};
		foreach (CharacterItemStorage storage in StorageList)
		{
			switch (storage.StorageType)
			{
			case StorageType.TOP:
				if (storage.ItemList.Count > 0)
				{
					string text2 = text;
					text = text2 + "アイテムバッグ（使用）: " + func(storage.ItemList) + "個\n";
				}
				break;
			case StorageType.BAG_MATERIAL:
				if (storage.ItemList.Count > 0)
				{
					string text2 = text;
					text = text2 + "アイテムバッグ（素材）: " + func(storage.ItemList) + "個\n";
				}
				break;
			case StorageType.STORAGE_ALL:
				if (storage.ItemList.Count > 0)
				{
					string text2 = text;
					text = text2 + "保管ボックス（通常）: " + func(storage.ItemList) + "個\n";
				}
				break;
			case StorageType.STORAGE_EX1_ALL:
				if (storage.ItemList.Count > 0)
				{
					string text2 = text;
					text = text2 + "保管ボックス（拡張）: " + func(storage.ItemList) + "個\n";
				}
				break;
			case StorageType.BAGGAGE_RENTAL01:
				if (storage.ItemList.Count > 0)
				{
					string text2 = text;
					text = text2 + "格納チェスト１: " + func(storage.ItemList) + "個\n";
				}
				break;
			case StorageType.BAGGAGE_RENTAL02:
				if (storage.ItemList.Count > 0)
				{
					string text2 = text;
					text = text2 + "格納チェスト２: " + func(storage.ItemList) + "個\n";
				}
				break;
			case StorageType.BAGGAGE_RENTAL03:
				if (storage.ItemList.Count > 0)
				{
					string text2 = text;
					text = text2 + "格納チェスト３: " + func(storage.ItemList) + "個\n";
				}
				break;
			}
		}
		return text;
	}
}
