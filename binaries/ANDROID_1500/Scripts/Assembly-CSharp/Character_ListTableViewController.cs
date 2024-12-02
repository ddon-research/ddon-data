using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

[RequireComponent(typeof(ScrollRect))]
public class Character_ListTableViewController : TableViewController<LoginCharacterList.ListElement>
{
	[SerializeField]
	private NavigationViewController navigationView;

	[SerializeField]
	private ViewController contentView;

	private void LoadData()
	{
		StartCoroutine(Uraguchi.Post(delegate(LoginCharacterList result)
		{
			TableData = new List<LoginCharacterList.ListElement>();
			foreach (LoginCharacterList.ListElement character in result.Characters)
			{
				TableData.Add(character);
			}
			UpdateContents();
		}, null, "masaki-nishimasu"));
	}

	protected override float CellHeightAtIndex(int index)
	{
		return 40f;
	}

	protected override void Awake()
	{
		base.Awake();
	}

	protected override void Start()
	{
		base.Start();
		if (navigationView != null)
		{
			navigationView.Push(this);
		}
	}

	private void OnEnable()
	{
		LoadData();
	}

	public void OnPressCell(MainMenuTableViewCell cell)
	{
		if (navigationView != null)
		{
			navigationView.Push(contentView);
		}
	}
}
