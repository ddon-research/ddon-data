using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(ScrollRect))]
public class PayMenuTableViewController : TableViewController<MainMenuData>
{
	[SerializeField]
	private NavigationViewController navigationView;

	[SerializeField]
	private ViewController contentView;

	public override string Title => "メニュー";

	private void LoadData()
	{
		TableData = new List<MainMenuData>
		{
			new MainMenuData
			{
				Type = MainMenuData.DataType.Header,
				Name = "メール",
				Description = "メール"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "受信",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "送信",
				Description = "メールの送信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Header,
				Name = "所持アイテム確認",
				Description = "メール"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "アイテムバッグ",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "保管ボックス",
				Description = "メールの送信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "自室のボックス",
				Description = "メールの送信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "アイテムポスト",
				Description = "メールの送信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Header,
				Name = "クラフト",
				Description = "メール"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "アイテム作成状況",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Header,
				Name = "バザー",
				Description = "メール"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "出品状態の確認",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Header,
				Name = "プレイヤー",
				Description = "メール"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "ステータス",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "クエストログ",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "エリアランク",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "アチーブメント",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Header,
				Name = "ポーン",
				Description = "メール"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "メインポーン",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "サポートポーン",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "ポーン検索",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "お気に入り",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Header,
				Name = "オンラインメンバー",
				Description = "メール"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "メンバーリスト",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Header,
				Name = "フレンド",
				Description = "メール"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "フレンドリスト",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Header,
				Name = "クラン",
				Description = "メール"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "クランステータス",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "クランメンバーリスト",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "クラン検索",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "クラン掲示板",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Header,
				Name = "ライブラリ",
				Description = "メール"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "エリアリスト",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "モンスター検索",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "クラフトレシピ",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "ジョブ",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "ジョブ修練",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Header,
				Name = "コンシェルジュポーン設定",
				Description = "メール"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "（工事中）",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Header,
				Name = "その他",
				Description = "メール"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "ヘルプ",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "設定",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "公式ページ",
				Description = "メールの受信"
			},
			new MainMenuData
			{
				Type = MainMenuData.DataType.Body,
				Name = "ライセンス",
				Description = "メールの受信"
			}
		};
		UpdateContents();
	}

	protected override float CellHeightAtIndex(int index)
	{
		if (TableData[index].Type == MainMenuData.DataType.Header)
		{
			return 28f;
		}
		return 40f;
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

	public void OnPressCell(PayMenuTableViewCell cell)
	{
		if (navigationView != null)
		{
			navigationView.Push(contentView);
		}
	}
}
