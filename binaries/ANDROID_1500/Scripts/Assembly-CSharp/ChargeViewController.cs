using System.Collections;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class ChargeViewController : ViewControllerAfterLoad
{
	[SerializeField]
	private Dropdown ControlDropdown;

	[SerializeField]
	private ScrollRect ScrollRect;

	[SerializeField]
	private Toggle AddTab;

	[SerializeField]
	private Toggle SubTab;

	private const uint ListMaxNum = 6u;

	private const uint ListMaxPage = 5u;

	private List<JemHistory> m_AddHistory = new List<JemHistory>();

	private List<JemHistory> m_SubHistory = new List<JemHistory>();

	private ChargeViewCell[] m_Cells;

	public void Initialize()
	{
		m_AddHistory.Clear();
		m_SubHistory.Clear();
		if (m_Cells == null)
		{
			m_Cells = GetComponentsInChildren<ChargeViewCell>();
		}
		ChargeViewCell[] cells = m_Cells;
		foreach (ChargeViewCell chargeViewCell in cells)
		{
			chargeViewCell.gameObject.SetActive(value: false);
		}
	}

	protected override IEnumerator LoadRoutine(ReqestResult result)
	{
		Initialize();
		yield return StartCoroutine(Charge.GetJemInfo(delegate(JemInfo res)
		{
			SingletonMonoBehaviour<ChargeManager>.Instance.SetJem(res.Jem);
			foreach (JemHistory item in res.AddHistory.History)
			{
				m_AddHistory.Add(item);
			}
			foreach (JemHistory item2 in res.SubHistory.History)
			{
				m_SubHistory.Add(item2);
			}
			AddTab.isOn = true;
			SetupList();
		}, delegate
		{
			result.isError = true;
		}, null, LoadingAnimation.Default));
	}

	private void SetupList()
	{
		uint num = 0u;
		if (AddTab.isOn)
		{
			num = (uint)m_AddHistory.Count / 6u;
			if (num == 0 || (uint)m_AddHistory.Count % 6u != 0)
			{
				num++;
			}
		}
		else
		{
			num = (uint)m_SubHistory.Count / 6u;
			if (num == 0 || (uint)m_SubHistory.Count % 6u != 0)
			{
				num++;
			}
		}
		ControlDropdown.options.Clear();
		for (uint num2 = 1u; num2 < num + 1; num2++)
		{
			ControlDropdown.options.Add(new Dropdown.OptionData(num2 + "/" + num));
		}
		ControlDropdown.value = 0;
		ControlDropdown.captionText.text = "1/" + num;
		UpdateList();
	}

	private void UpdateList(int pageNum = 0)
	{
		List<JemHistory> list = null;
		ChargeViewCell.BgType bgType;
		if (AddTab.isOn)
		{
			list = m_AddHistory;
			bgType = ChargeViewCell.BgType.Pattern00;
		}
		else
		{
			list = m_SubHistory;
			bgType = ChargeViewCell.BgType.Pattern01;
		}
		int num = pageNum * m_Cells.Length;
		ChargeViewCell[] cells = m_Cells;
		foreach (ChargeViewCell chargeViewCell in cells)
		{
			if (list.Count <= num)
			{
				chargeViewCell.gameObject.SetActive(value: false);
				continue;
			}
			chargeViewCell.gameObject.SetActive(value: true);
			chargeViewCell.UpdateContent(list[num], bgType);
			num++;
		}
	}

	public void OnChangeTab()
	{
		SetupList();
	}

	public void OnPushControlLeft()
	{
		if (ControlDropdown.value > 0)
		{
			ControlDropdown.value--;
		}
	}

	public void OnPushControlRight()
	{
		if (ControlDropdown.value < ControlDropdown.options.Count - 1)
		{
			ControlDropdown.value++;
		}
	}

	public void OnChangeDropdown()
	{
		UpdateList(ControlDropdown.value);
	}

	public void OnPushWebLeft()
	{
		Application.OpenURL("https://members.dd-on.jp/app/support/settlement.html/");
	}

	public void OnPushWebRight()
	{
		Application.OpenURL("https://members.dd-on.jp/app/support/transaction.html/");
	}
}
