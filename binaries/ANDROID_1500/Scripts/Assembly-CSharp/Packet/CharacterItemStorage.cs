using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class CharacterItemStorage
{
	public StorageType StorageType;

	public List<StorageItem> ItemList = new List<StorageItem>();

	public bool IsAvailable;
}
