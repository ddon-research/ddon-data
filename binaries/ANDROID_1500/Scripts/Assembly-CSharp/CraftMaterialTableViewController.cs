using Packet;

public class CraftMaterialTableViewController : TableViewController<CraftMaterialData>
{
	public void LoadData(CraftRecipeDetail detail)
	{
		Initialize();
		TableData.Clear();
		foreach (CraftRecipeMaterial material in detail.Materials)
		{
			CraftMaterialData craftMaterialData = new CraftMaterialData();
			craftMaterialData.ItemName = material.Item.Name;
			craftMaterialData.ItemsId = material.Item.ItemID;
			craftMaterialData.IconName = material.Item.IconName;
			craftMaterialData.IconColorId = material.Item.IconColorId;
			craftMaterialData.NeedNum = material.Num;
			craftMaterialData.SelectedNum = SingletonMonoBehaviour<CraftManager>.Instance.GetMaterialNum(material.Item.ItemID);
			TableData.Add(craftMaterialData);
		}
		UpdateContents();
	}

	public void RefreshSelectedNum()
	{
		foreach (CraftMaterialData tableDatum in TableData)
		{
			tableDatum.SelectedNum = SingletonMonoBehaviour<CraftManager>.Instance.GetMaterialNum(tableDatum.ItemsId);
		}
	}
}
