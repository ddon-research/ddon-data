using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class BazaarBuyTableViewCell : TableViewCell<BazaarExhibitElement>
{
	[SerializeField]
	private Text UnitPriceText;

	[SerializeField]
	private Text NumText;

	[SerializeField]
	private Text PriceText;

	[SerializeField]
	private ViewController AcceptedView;

	public BazaarExhibitElement Data;

	private void Start()
	{
		Button component = GetComponent<Button>();
		if (component != null)
		{
			component.onClick.AddListener(OnClick);
		}
	}

	public override void UpdateContent(BazaarExhibitElement itemData)
	{
		Data = itemData;
		UnitPriceText.text = itemData.UnitPrice.ToString("N0");
		NumText.text = itemData.Num.ToString();
		PriceText.text = itemData.Price.ToString("N0");
	}

	public void OnClick()
	{
		SingletonMonoBehaviour<UseJemDialog>.Instance.Show("アイテムを購入", 1u, delegate(bool retBuy)
		{
			if (retBuy)
			{
				if (SingletonMonoBehaviour<ChargeManager>.Instance.GetToralJem() < 1)
				{
					SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "黄金石のカケラが不足しています");
				}
				else if (SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData.Gold < Data.Price)
				{
					SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "所持ゴールドが不足しています");
				}
				else
				{
					StartCoroutine(Bazaar.PostBuyItem(delegate(BazaarBuyResult result)
					{
						ItemStorage.ClearCache();
						SingletonMonoBehaviour<ChargeManager>.Instance.SetJem(result.JemList);
						MainViewController.Instance.SetCharacterGold(result.Gold);
						AcceptedView.Push();
					}, null, Data, LoadingAnimation.Default));
				}
			}
		});
	}
}
