using System;
using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class CraftSituationTableViewCell : TableViewCell<CraftPawnStatus>
{
	[SerializeField]
	private Text PawnNameText;

	[SerializeField]
	private Text CraftLvText;

	[SerializeField]
	private Text RemainTimeText;

	[SerializeField]
	private ItemIcon ProductItemIcon;

	[SerializeField]
	private Text ProductItemNameText;

	[SerializeField]
	private Image IconDone;

	[SerializeField]
	private Button InterruptButton;

	[SerializeField]
	private CraftSituationTableViewController TableView;

	[SerializeField]
	private Text EndText;

	private CraftPawnStatus Data;

	private void Start()
	{
		InterruptButton.onClick.AddListener(InterruptCraft);
	}

	public override void UpdateContent(CraftPawnStatus itemData)
	{
		Data = itemData;
		PawnNameText.text = itemData.PawnName;
		CraftLvText.text = itemData.CraftLv.ToString();
		ProductItemIcon.Load(itemData.ProductItem.IconName, itemData.ProductItem.IconColorId);
		ProductItemNameText.text = itemData.ProductItem.Name;
		IconDone.gameObject.SetActive(value: false);
		InterruptButton.gameObject.SetActive(value: true);
		EndText.gameObject.SetActive(value: false);
		TimeSpan timeSpan = TimeSpan.FromSeconds(itemData.RemainTime);
		uint num = (uint)timeSpan.TotalHours;
		if (num != 0)
		{
			RemainTimeText.text = num + "h" + timeSpan.Minutes + "m";
		}
		else if (timeSpan.TotalSeconds > 0.0)
		{
			if (timeSpan.Minutes == 0)
			{
				RemainTimeText.text = "1m";
			}
			else
			{
				RemainTimeText.text = timeSpan.Minutes + "m";
			}
		}
		else
		{
			RemainTimeText.text = string.Empty;
			IconDone.gameObject.SetActive(value: true);
			InterruptButton.gameObject.SetActive(value: false);
			EndText.gameObject.SetActive(value: true);
		}
	}

	public void ToItemDetail()
	{
	}

	public void InterruptCraft()
	{
		SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK_Cancel, "確認", "クラフトを中断しますか？\n\n<color=#d94d4d><size=24>※黄金石の\rカケラ・素材・費用・\nクラフト回数は消費されます</size></color>", delegate(ModalDialog.Result res)
		{
			if (res == ModalDialog.Result.OK)
			{
				StartCoroutine(Craft.PostInterrupt(delegate
				{
					Craft.ClearCache_GetPawn();
					Craft.ClearCache_GetSupportPawn();
					Craft.ClearCache_GetPawnStatus();
					TableView.LoadData();
					SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "クラフトを中断しました。");
				}, null, Data.MyPawnID, Data.RecipeID, Data.FinishTime, LoadingAnimation.Default));
			}
		});
	}
}
