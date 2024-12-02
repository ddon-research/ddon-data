using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class PresentBoxTableViewController : TableViewController<CharacterGift>
{
	[SerializeField]
	private Button ReceiveButton;

	[SerializeField]
	private Text EmptyText;

	private void Update()
	{
		if (!(ReceiveButton != null))
		{
			return;
		}
		if (cells.Count <= 0)
		{
			if (ReceiveButton.interactable)
			{
				ReceiveButton.interactable = false;
			}
		}
		else if (!ReceiveButton.interactable)
		{
			ReceiveButton.interactable = true;
		}
	}

	private void OnEnable()
	{
		UpdateList();
	}

	private void UpdateList()
	{
		Initialize();
		StartCoroutine(Gift.GetGiftList(delegate(CharacterGiftList res)
		{
			if (res.Gift.Count > 0)
			{
				EmptyText.enabled = false;
			}
			else
			{
				EmptyText.enabled = true;
			}
			foreach (CharacterGift item in res.Gift)
			{
				TableData.Add(item);
			}
			UpdateContents();
			SingletonMonoBehaviour<ProfileManager>.Instance.ReceiveGiftNum = (uint)res.Gift.Count;
		}, null, null, LoadingAnimation.Default));
	}

	public void ReceiveGiftAll()
	{
		Initialize();
		StartCoroutine(Gift.PostReceiveGiftAll(delegate(ReceiveGift res)
		{
			SingletonMonoBehaviour<ChargeManager>.Instance.SetJem(res.Jem);
			GetGiftjem(res.Gift, out var payValue, out var freeValue);
			string text = string.Empty;
			if (res.Gift.Count > 0)
			{
				text = "下記のアイテムを受け取りました\n\n";
				if (payValue != 0)
				{
					text = text + "黄金石のカケラ（購入分）×" + payValue.ToString("N0");
				}
				if (freeValue != 0)
				{
					text = text + "黄金石のカケラ（無料分）×" + freeValue.ToString("N0");
				}
			}
			if (!res.IsReceive)
			{
				text = ((text.Length <= 0) ? (text + "所持できる上限を超えたため\nプレゼントを受け取れませんでした") : (text + "\n\n所持できる上限を超えたため\n一部のプレゼントが\n受け取れませんでした"));
			}
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "プレゼント取得", text, delegate
			{
				UpdateList();
			});
		}, null, SingletonMonoBehaviour<ChargeManager>.Instance.Platform, LoadingAnimation.Default));
	}

	public void ReceiveGift(uint id)
	{
		Initialize();
		StartCoroutine(Gift.PostReceiveGift(delegate(ReceiveGift res)
		{
			SingletonMonoBehaviour<ChargeManager>.Instance.SetJem(res.Jem);
			string empty = string.Empty;
			if (res == null || !res.IsReceive)
			{
				empty += "所持できる上限を超えたため\nプレゼントを受け取れませんでした";
			}
			else
			{
				GetGiftjem(res.Gift, out var payValue, out var freeValue);
				empty = "下記のアイテムを受け取りました\n\n";
				if (payValue != 0)
				{
					empty = empty + "黄金石のカケラ（購入分）×" + payValue.ToString("N0");
				}
				if (freeValue != 0)
				{
					empty = empty + "黄金石のカケラ（無料分）×" + freeValue.ToString("N0");
				}
			}
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "プレゼント取得", empty, delegate
			{
				UpdateList();
			});
		}, null, id, SingletonMonoBehaviour<ChargeManager>.Instance.Platform, LoadingAnimation.Default));
	}

	private void GetGiftjem(List<CharacterGift> list, out ulong payValue, out ulong freeValue)
	{
		payValue = 0uL;
		freeValue = 0uL;
		foreach (CharacterGift item in list)
		{
			foreach (CharacterGiftJem jem in item.Jems)
			{
				if (jem.Type == JemType.PAY)
				{
					payValue += (ulong)jem.Value;
				}
				if (jem.Type == JemType.FREE)
				{
					freeValue += (ulong)jem.Value;
				}
			}
		}
	}
}
