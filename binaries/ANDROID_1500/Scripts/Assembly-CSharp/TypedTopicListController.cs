using System;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.UI;

public class TypedTopicListController : TableViewController<CalendarTopic>
{
	[SerializeField]
	private float CellItemHeight = 150f;

	[SerializeField]
	private RectTransform ContentHolder;

	[SerializeField]
	private ReloadChecker MyReloadChecker;

	private bool IsInit;

	[SerializeField]
	private Text EmptyText;

	public void Init(Action callback = null)
	{
		MyReloadChecker.Init(callback);
		ContentHolder.anchoredPosition = new Vector2(ContentHolder.anchoredPosition.x, 0f);
	}

	public void MarkShowReload(bool flag)
	{
		if (flag)
		{
			MyReloadChecker.MarkShowReload();
		}
		else
		{
			MyReloadChecker.MarkHideReload();
		}
	}

	protected override float CellHeightAtIndex(int index)
	{
		return CellItemHeight;
	}

	protected override void Awake()
	{
		base.Awake();
	}

	protected override void Start()
	{
		base.Start();
	}

	public override void OnNavigationPushEnd()
	{
	}

	public override void OnNavigationPopBegin()
	{
		TableData.Clear();
		ContentHolder.anchoredPosition = new Vector2(ContentHolder.anchoredPosition.x, 0f);
	}

	public void SetUpdateContents()
	{
		UpdateContents();
		if (TableData.Count == 0)
		{
			EmptyText.gameObject.SetActive(value: true);
		}
		else
		{
			EmptyText.gameObject.SetActive(value: false);
		}
	}

	public void TableAdd(CalendarTopic topic)
	{
		TableData.Add(topic);
	}

	public void TableClear()
	{
		TableData.Clear();
	}

	public List<CalendarTopic> GetTableList()
	{
		return TableData;
	}
}
