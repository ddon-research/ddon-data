using System.Collections.Generic;
using Packet;

public class ChargeManager : SingletonMonoBehaviour<ChargeManager>
{
	public enum JemDispType
	{
		TOTAL,
		PAY,
		FREE
	}

	private List<CharacterJem> m_JemList = new List<CharacterJem>();

	private string[] ActivitieName = new string[9]
	{
		string.Empty,
		"ログインボーナス",
		"リサの贈り物",
		"運営からのプレゼント",
		"運営からの補填",
		"メール送信",
		"クラフトアイテム作成",
		"バザー購入",
		"バザー出品"
	};

	public PlatformID Platform { get; set; }

	private void Start()
	{
		Platform = PlatformID.ANDROID;
	}

	public void Reset()
	{
		m_JemList.Clear();
	}

	public void SetJem(CharacterJemList list)
	{
		m_JemList.Clear();
		foreach (CharacterJem item in list.Jem)
		{
			m_JemList.Add(item);
		}
	}

	public long GetToralJem()
	{
		long num = 0L;
		foreach (CharacterJem jem in m_JemList)
		{
			num += (long)jem.Value;
		}
		return num;
	}

	public long GetPayJem()
	{
		long num = 0L;
		foreach (CharacterJem jem in m_JemList)
		{
			if (jem.Type == JemType.PAY)
			{
				num += (long)jem.Value;
			}
		}
		return num;
	}

	public long GetFreeJem()
	{
		long num = 0L;
		foreach (CharacterJem jem in m_JemList)
		{
			if (jem.Type == JemType.FREE)
			{
				num += (long)jem.Value;
			}
		}
		return num;
	}

	public string GetActivitieName(JemActivitie activitie)
	{
		if (ActivitieName.Length <= (uint)activitie)
		{
			return string.Empty;
		}
		return ActivitieName[(int)activitie];
	}
}
