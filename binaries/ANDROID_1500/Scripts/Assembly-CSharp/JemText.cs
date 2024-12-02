using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(Text))]
public class JemText : MonoBehaviour
{
	public ChargeManager.JemDispType m_Type;

	public long m_MaxValue = 9999999999L;

	private long m_Value;

	private Text m_Text;

	private void Start()
	{
		m_Text = GetComponent<Text>();
		InitText();
	}

	private void Update()
	{
		if (CheckText())
		{
			UpdateText();
		}
	}

	private bool CheckText()
	{
		long num = 0L;
		switch (m_Type)
		{
		case ChargeManager.JemDispType.TOTAL:
			num = SingletonMonoBehaviour<ChargeManager>.Instance.GetToralJem();
			break;
		case ChargeManager.JemDispType.PAY:
			num = SingletonMonoBehaviour<ChargeManager>.Instance.GetPayJem();
			break;
		case ChargeManager.JemDispType.FREE:
			num = SingletonMonoBehaviour<ChargeManager>.Instance.GetFreeJem();
			break;
		}
		if (num < 0)
		{
			num = 0L;
		}
		if (num > m_MaxValue)
		{
			num = m_MaxValue;
		}
		if (num != m_Value)
		{
			m_Value = num;
			return true;
		}
		return false;
	}

	private void InitText()
	{
		m_Value = -1L;
		m_Text.text = "0";
	}

	private void UpdateText()
	{
		string text = m_Value.ToString("N0");
		m_Text.text = text;
	}
}
