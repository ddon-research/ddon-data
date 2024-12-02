using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;

public class BackImageSelector : MonoBehaviour
{
	private List<BackImageItem> itemList = new List<BackImageItem>();

	[SerializeField]
	private BackImageItem BackImageItemPrefab;

	[SerializeField]
	private BackImageDataTable BackImageTable;

	[SerializeField]
	private int CurrentIndex = 1;

	[SerializeField]
	private UnityEvent OnEnableCallback;

	[SerializeField]
	private UnityEvent OnValueChangeCallback;

	public void Init()
	{
		for (int i = 0; i < BackImageTable.BackImageList.Length; i++)
		{
			string thumbPath = BackImageTable.BackImageList[i];
			BackImageItem backImageItem = Object.Instantiate(BackImageItemPrefab);
			backImageItem.transform.parent = base.transform;
			backImageItem.gameObject.transform.localScale = new Vector3(1f, 1f, 1f);
			backImageItem.UpdateContent(i, thumbPath);
			itemList.Add(backImageItem);
			backImageItem.Select(flag: false);
		}
		itemList[1].Select(flag: true);
		CurrentIndex = 1;
		int calendarBGImage = PlayerPerfManager.GetCalendarBGImage();
		if (calendarBGImage < itemList.Count)
		{
			itemList[1].Select(flag: false);
			itemList[calendarBGImage].Select(flag: true);
			CurrentIndex = calendarBGImage;
		}
	}

	public void OnEnable()
	{
		OnEnableCallback.Invoke();
	}

	public void AllOff()
	{
		OnValueChangeCallback.Invoke();
		foreach (BackImageItem item in itemList)
		{
			item.Select(flag: false);
		}
	}

	public void OnDisable()
	{
		if (itemList.Count > CurrentIndex)
		{
			ResetIndex(CurrentIndex);
		}
	}

	private void ResetIndex(int index)
	{
		AllOff();
		itemList[index].Select(flag: true);
	}

	public int GetIndex()
	{
		return CurrentIndex;
	}

	private int GetIndexSelected()
	{
		foreach (BackImageItem item in itemList)
		{
			if (item.IsSelected)
			{
				return item.BackImageIndex;
			}
		}
		return 1;
	}

	public string GetPath()
	{
		int index = GetIndex();
		if (index >= BackImageTable.BackImageList.Length)
		{
			return BackImageTable.BackImageList[1];
		}
		return BackImageTable.BackImageList[index];
	}

	public void OnSave()
	{
		PlayerPerfManager.SetCalendarBGImage(CurrentIndex = GetIndexSelected());
		SingletonMonoBehaviour<AppUtility>.Instance.ShowDialogAndPop("確認", "カレンダー壁紙設定を保存しました。", delegate
		{
			SingletonMonoBehaviour<CalendarManager>.Instance.BackImageController.MarkReload();
		});
	}
}
