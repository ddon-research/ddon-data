using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class BazaarExhibitRequest
{
	public uint ItemId;

	public uint Price;

	public List<StorageSlotItem> ExhibitItems = new List<StorageSlotItem>();
}
