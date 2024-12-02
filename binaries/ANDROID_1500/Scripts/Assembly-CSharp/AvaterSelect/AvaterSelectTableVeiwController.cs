using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace AvaterSelect;

[RequireComponent(typeof(ScrollRect))]
public class AvaterSelectTableVeiwController : TableViewController<Data>
{
	[SerializeField]
	private NavigationViewController navigationView;

	[SerializeField]
	private ViewController contentView;

	public override string Title => "メニュー";

	private void LoadData()
	{
		TableData = new List<Data>();
		uint num = SingletonMonoBehaviour<ProfileManager>.Instance.CharacterIconMax / 4 + 1;
		for (uint num2 = 0u; num2 < num; num2++)
		{
			Data data = new Data();
			data.RowIndex = num2;
			for (uint num3 = 0u; num3 < 4; num3++)
			{
				data.IconIDs[num3] = num2 * 4 + num3;
			}
			TableData.Add(data);
		}
		UpdateContents();
	}

	protected override float CellHeightAtIndex(int index)
	{
		return 150f;
	}

	protected override void Awake()
	{
		base.Awake();
	}

	protected override void Start()
	{
		base.Start();
		LoadData();
		if (navigationView != null)
		{
			navigationView.Push(this);
		}
	}

	public void OnPressCell(MainMenuTableViewCell cell)
	{
		if (navigationView != null)
		{
			navigationView.Push(contentView);
		}
	}
}
