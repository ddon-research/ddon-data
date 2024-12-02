using System;
using Packet;
using WebRequest;

public class LoginBonusManager : SingletonMonoBehaviour<LoginBonusManager>
{
	private const uint LoginBonusResetTime = 5u;

	private DateTime m_NextCheckTime = default(DateTime);

	private void Start()
	{
		m_NextCheckTime = DateTime.MinValue;
	}

	public void CheckLoginBonus()
	{
		if (DateTime.Now < m_NextCheckTime)
		{
			return;
		}
		m_NextCheckTime = DateTime.Now.AddHours(-5.0).Date.AddDays(1.0).AddHours(5.0);
		StartCoroutine(LoginBonus.PostCheckDailyBonus(delegate(CharacterDailyBonusList ret)
		{
			if (ret.Bonus.Count > 0)
			{
				string text = string.Empty;
				foreach (CharacterDailyBonus bonu in ret.Bonus)
				{
					text = text + "黄金石のカケラ×" + ret.Bonus[0].JemValue.ToString("N0") + "\n";
				}
				text += "を取得しました。\n";
				text += "ログインボーナスはプレゼントボックスから受け取れます。";
				SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "ログインボーナス", text);
				SingletonMonoBehaviour<ProfileManager>.Instance.ReceiveGiftNum += (uint)ret.Bonus.Count;
			}
		}, delegate
		{
			m_NextCheckTime = DateTime.MinValue;
		}));
	}
}
