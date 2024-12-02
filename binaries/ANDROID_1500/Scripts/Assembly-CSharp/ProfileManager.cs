using System;
using Packet;
using UnityEngine;
using WebRequest;

public class ProfileManager : SingletonMonoBehaviour<ProfileManager>
{
	protected class StatusBase
	{
		public string Name;

		public byte JobId;

		public ushort JobLevel;

		public uint ItemRank;
	}

	[SerializeField]
	private Sprite[] IconSex;

	[SerializeField]
	private Sprite[] ClanMark;

	[SerializeField]
	private Sprite[] ClanBase;

	[SerializeField]
	private Color[] ClanEmbelmColor;

	public Sprite DefaultCharacterIcon;

	public uint CharacterIconMax;

	[SerializeField]
	private PlayerViewController MyPlayerView;

	[SerializeField]
	private PlayerViewController OtherPlayerView;

	[SerializeField]
	private MainPawnViewController MainPawnView;

	[SerializeField]
	private OtherPawnViewController MainOtherPawnView;

	[SerializeField]
	private SupportPawnViewController SupportPawnView;

	private StatusBase m_StatusBase = new StatusBase();

	private string[] m_PlayPurpose = new string[6] { "とくになし", "レベルあげ", "お金を稼ぐ", "素材集め", "オーブエネミーを倒す", "イベントで遊ぶ" };

	private string[] m_PlayStyle = new string[28]
	{
		"指定なし", "まったりあそぼう", "戦闘大好き", "お金大好き", "クエスト攻略大好き", "ミッション攻略大好き", "限定イベント大好き", "シナリオ大好き", "クラフト大好き", "ランキング大好き",
		"アタッカーでプレイしています！", "タンクでプレイしています！", "ヒーラーでプレイしています！", "複数ジョブでプレイしています！", "ポーンを混ぜてパーティを組もう", "朝方中心プレイ", "昼型中心プレイ", "夜型中心プレイ", "いつでもプレイ", "平日中心プレイ",
		"週末中心プレイ", "休日中心プレイ", "毎日プレイ", "不定期にコツコツプレイ", "フレンド募集中", "クランに入りたい", "クランメンバー募集中", "グループチャットに入りたい"
	};

	private const string EventTimeKey = "ddo_event_time_key";

	private DateTime EventLastCheckTime = DateTime.MinValue;

	public string StatusName => m_StatusBase.Name;

	public byte StatusJobId => m_StatusBase.JobId;

	public ushort StatusJobLevel => m_StatusBase.JobLevel;

	public uint StatusItemRank => m_StatusBase.ItemRank;

	public CharacterDataBase CharacterData { get; private set; }

	public uint ReceiveGiftNum
	{
		get
		{
			return CharacterData.GiftNum;
		}
		set
		{
			CharacterData.GiftNum = value;
		}
	}

	public void SetStatusBase(string name, byte jobId, ushort jobLevel, uint itemRank)
	{
		m_StatusBase.Name = name;
		m_StatusBase.JobId = jobId;
		m_StatusBase.JobLevel = jobLevel;
		m_StatusBase.ItemRank = itemRank;
	}

	public void SetCharacterData(CharacterDataBase data)
	{
		CharacterData = data;
	}

	public void CheckAnnounce()
	{
		StartCoroutine(WebRequest.CharacterData.GetAnnounce(delegate(CharacterAnnounce ret)
		{
			ReceiveGiftNum = ret.GiftNum;
		}, delegate
		{
			ReceiveGiftNum = 0u;
		}));
	}

	public Sprite GetSexIcon(uint id)
	{
		if (IconSex == null || IconSex.Length <= --id)
		{
			return null;
		}
		return IconSex[id];
	}

	public Sprite GetClanMark(ushort id)
	{
		if (ClanMark == null || ClanMark.Length <= --id)
		{
			return null;
		}
		return ClanMark[id];
	}

	public Sprite GetClanBase(ushort id)
	{
		if (ClanBase == null || ClanBase.Length <= --id)
		{
			return null;
		}
		return ClanBase[id];
	}

	public Color GetClanEmblemColor(ushort id)
	{
		if (ClanEmbelmColor == null || ClanEmbelmColor.Length <= --id)
		{
			return Color.white;
		}
		return ClanEmbelmColor[id];
	}

	public string GetPlayPurposName(uint id)
	{
		if (--id >= m_PlayPurpose.Length)
		{
			return string.Empty;
		}
		return m_PlayPurpose[id];
	}

	public string GetPlayStyleName(uint id)
	{
		if (--id >= m_PlayStyle.Length)
		{
			return string.Empty;
		}
		return m_PlayStyle[id];
	}

	public void OpenProfileMyPlayer()
	{
		if (MyPlayerView != null && !MyPlayerView.gameObject.activeSelf)
		{
			MyPlayerView.CharacterId = CharacterData.CharacterID;
			MyPlayerView.Push();
		}
	}

	public void OpenProfilePlayer(uint characterId)
	{
		PlayerViewController playerViewController = null;
		playerViewController = ((CharacterData.CharacterID != characterId) ? OtherPlayerView : MyPlayerView);
		if (playerViewController != null && !playerViewController.gameObject.activeSelf)
		{
			playerViewController.CharacterId = characterId;
			playerViewController.Push();
		}
	}

	public void OpenProfileMainPawn(uint characterId, uint pawnId)
	{
		if (characterId == CharacterData.CharacterID)
		{
			if (MainPawnView != null && !MainPawnView.gameObject.activeSelf)
			{
				MainPawnView.PawnId = pawnId;
				MainPawnView.Push();
			}
		}
		else if (MainOtherPawnView != null && !MainOtherPawnView.gameObject.activeSelf)
		{
			MainOtherPawnView.PawnId = pawnId;
			MainOtherPawnView.Push();
		}
	}

	public void OpenProfileSupportPawn(uint pawnId)
	{
		if (SupportPawnView != null && !SupportPawnView.gameObject.activeSelf)
		{
			SupportPawnView.CharacterId = CharacterData.CharacterID;
			SupportPawnView.PawnId = pawnId;
			SupportPawnView.Push();
		}
	}

	public bool CanCraft()
	{
		return CharacterData.canCraft;
	}

	public bool CheckNewEvent()
	{
		DateTime dateTime;
		try
		{
			dateTime = DateTime.FromBinary(CharacterData.EventTime);
		}
		catch (Exception)
		{
			dateTime = DateTime.MinValue;
		}
		if (dateTime > EventLastCheckTime)
		{
			return true;
		}
		return false;
	}

	private void Start()
	{
		try
		{
			string @string = PlayerPrefs.GetString("ddo_event_time_key");
			EventLastCheckTime = DateTime.FromBinary(Convert.ToInt64(@string));
		}
		catch (Exception)
		{
			EventLastCheckTime = DateTime.MinValue;
		}
	}

	public void UpdateEventLastCheckTime()
	{
		EventLastCheckTime = DateTime.Now;
		PlayerPrefs.SetString("ddo_event_time_key", EventLastCheckTime.ToBinary().ToString());
	}

	public void ResetEventLastCheckTime()
	{
		PlayerPrefs.SetString("ddo_event_time_key", DateTime.MinValue.ToBinary().ToString());
	}
}
