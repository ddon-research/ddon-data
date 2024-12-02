using System;

namespace Packet;

[Serializable]
public class BazaarExhibitElement
{
	public ulong ID;

	public uint Price;

	public uint UnitPrice;

	public ushort Num;

	public ushort Seq;

	public BazaarExhibitElement()
	{
	}

	public BazaarExhibitElement(ulong id, ushort num, uint unitPrice, ushort seq)
	{
		ID = id;
		Num = num;
		UnitPrice = unitPrice;
		Price = UnitPrice * Num;
		Seq = seq;
	}

	public BazaarExhibitElement Clone()
	{
		BazaarExhibitElement bazaarExhibitElement = new BazaarExhibitElement();
		bazaarExhibitElement.ID = ID;
		bazaarExhibitElement.Price = Price;
		bazaarExhibitElement.UnitPrice = UnitPrice;
		bazaarExhibitElement.Num = Num;
		bazaarExhibitElement.Seq = Seq;
		return bazaarExhibitElement;
	}
}
