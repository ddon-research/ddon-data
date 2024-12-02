using Packet;
using WebRequest;

public class CraftRefineItemTableViewController : TableViewController<ItemData>
{
	private void OnEnable()
	{
		Initialize();
		if (SingletonMonoBehaviour<CraftManager>.Instance.MainCategory == CraftMainCategory.Weapon)
		{
			StartCoroutine(ItemParam.GetWeaponRefineItems(delegate(ItemDataList ret)
			{
				foreach (ItemData item in ret.ItemList)
				{
					TableData.Add(item);
				}
				UpdateContents();
			}, null, CacheOption.OneHour, LoadingAnimation.Default));
		}
		else
		{
			if (SingletonMonoBehaviour<CraftManager>.Instance.MainCategory != CraftMainCategory.Protection)
			{
				return;
			}
			StartCoroutine(ItemParam.GetProtecterRefineItems(delegate(ItemDataList ret)
			{
				foreach (ItemData item2 in ret.ItemList)
				{
					TableData.Add(item2);
				}
				UpdateContents();
			}, null, CacheOption.OneHour, LoadingAnimation.Default));
		}
	}
}
