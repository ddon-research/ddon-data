using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class BazaarExhibitElementList
{
	public uint ItemId;

	public string ItemName;

	public List<BazaarExhibitElement> Items = new List<BazaarExhibitElement>();

	public BazaarExhibitElementList Clone()
	{
		BazaarExhibitElementList bazaarExhibitElementList = new BazaarExhibitElementList();
		bazaarExhibitElementList.ItemId = ItemId;
		bazaarExhibitElementList.ItemName = ItemName;
		foreach (BazaarExhibitElement item in Items)
		{
			bazaarExhibitElementList.Items.Add(item.Clone());
		}
		return bazaarExhibitElementList;
	}
}
