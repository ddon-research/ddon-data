using System;
using System.Collections;
using UnityEngine;

public static class ItemIconManager
{
	public static IEnumerator LoadIcon(string iconName, uint colorId, Action<Sprite> onLoadImage, Action<Sprite> onLoadColor)
	{
		string path2 = "Images/itembg/" + colorId;
		yield return LoadManager.LoadAsync(path2, delegate(Sprite res)
		{
			onLoadColor(res);
		});
		string path = "Images/itemicon/icon_" + iconName + "_ID";
		yield return LoadManager.LoadAsync(path, delegate(Sprite res)
		{
			onLoadImage(res);
		});
	}
}
