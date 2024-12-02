using System.Collections.Generic;

namespace Packet;

public class CraftRequest
{
	public uint RecipeID;

	public List<StorageSlotItem> MaterialItems = new List<StorageSlotItem>();

	public uint MyPawnID;

	public List<uint> AssistMyPawns = new List<uint>();

	public List<uint> AssistRentalPawns = new List<uint>();

	public StorageSlotItem RefineItem = new StorageSlotItem();

	public uint DoNum;
}
