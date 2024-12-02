using System;
using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class BazaarExhibitStatusController : ViewController
{
	[SerializeField]
	private BazaarExhibitStatusTableViewController TableView;

	[SerializeField]
	private Text ExhibitingNum;

	[SerializeField]
	private Text TotalEarnings;

	[SerializeField]
	private Button AllEarningsReceiveButton;

	private BazaarExhibitingStatus Statuses;

	public void ReceiveAllEarnings()
	{
		SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK_Cancel, "確認", "全ての売り上げを受け取ります。\nよろしいですか？", delegate(ModalDialog.Result res)
		{
			if (res == ModalDialog.Result.OK)
			{
				BazaarRceivePrceedsRequest bazaarRceivePrceedsRequest = new BazaarRceivePrceedsRequest();
				uint total = 0u;
				foreach (BazaarExhibitingElement element in Statuses.Elements)
				{
					if (element.Status == E_BAZAAR_STATE.BAZAAR_STATE_PROCEEDS)
					{
						bazaarRceivePrceedsRequest.IDList.Add(element.ID);
						total += element.Proceeds;
					}
				}
				StartCoroutine(Bazaar.PostReceiveProceeds(delegate(BazaarReceiveProceedsResult receiveResult)
				{
					Bazaar.ClearCache_GetExhibitListUInt32();
					MainViewController.Instance.SetCharacterGold(receiveResult.Gold);
					SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", total + "Gを受け取りました", delegate
					{
						LoadList();
					});
				}, null, bazaarRceivePrceedsRequest, LoadingAnimation.Default));
			}
		});
	}

	private void OnEnable()
	{
		LoadList();
	}

	public void InterruptExhibit(ulong id)
	{
		StartCoroutine(Bazaar.PostInterrupt(delegate
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "出品をキャンセルしました。商品はメールでお受け取りください");
			LoadList();
		}, null, id, LoadingAnimation.Default));
	}

	private void LoadList()
	{
		TableView.Initialize();
		AllEarningsReceiveButton.gameObject.SetActive(value: false);
		ExhibitingNum.text = string.Empty;
		TotalEarnings.text = string.Empty;
		StartCoroutine(Bazaar.GetCharacterBazaarList(delegate(BazaarExhibitingStatus res)
		{
			Statuses = res;
			uint num = 0u;
			uint num2 = 0u;
			bool flag = false;
			foreach (BazaarExhibitingElement element in res.Elements)
			{
				if (element.Status == E_BAZAAR_STATE.BAZAAR_STATE_PROCEEDS)
				{
					num += element.Proceeds;
					flag = true;
					num2++;
				}
				TimeSpan timeSpan = TimeSpan.FromSeconds(element.RemainTime);
				if (element.Status == E_BAZAAR_STATE.BAZAAR_STATE_EXHIBITING && timeSpan.TotalSeconds > 0.0)
				{
					num2++;
				}
			}
			ExhibitingNum.text = num2.ToString();
			if (flag)
			{
				AllEarningsReceiveButton.gameObject.SetActive(value: true);
			}
			TotalEarnings.text = num.ToString("N0");
			TableView.SetData(res);
		}, null, null, LoadingAnimation.Default));
	}
}
