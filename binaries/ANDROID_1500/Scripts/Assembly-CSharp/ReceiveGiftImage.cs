using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class ReceiveGiftImage : MonoBehaviour
{
	[SerializeField]
	private Text Number;

	[SerializeField]
	private GameObject Content;

	[SerializeField]
	private Image Left;

	[SerializeField]
	private Image Right;

	[SerializeField]
	private Image Body;

	private uint m_Num;

	private uint m_MaxNum = 99u;

	private List<Image> m_BodyList = new List<Image>();

	private void Awake()
	{
		m_Num = 0u;
		Content.SetActive(value: false);
		m_BodyList.Add(Body);
		Body.gameObject.SetActive(value: false);
		uint num = m_MaxNum;
		while (num != 0)
		{
			num /= 10;
			if (num != 0)
			{
				Image image = Object.Instantiate(Body);
				image.rectTransform.SetParent(Body.transform.parent.transform, worldPositionStays: false);
				image.gameObject.SetActive(value: false);
				m_BodyList.Add(image);
			}
		}
		Right.transform.SetAsLastSibling();
		Left.transform.SetAsFirstSibling();
	}

	private void Update()
	{
		bool flag = false;
		uint num = SingletonMonoBehaviour<ProfileManager>.Instance.ReceiveGiftNum;
		if (num > m_MaxNum)
		{
			num = m_MaxNum;
			flag = true;
		}
		if (num == m_Num)
		{
			return;
		}
		m_Num = num;
		if (m_Num == 0)
		{
			Content.SetActive(value: false);
			return;
		}
		Content.SetActive(value: true);
		string text = m_Num.ToString();
		if (flag)
		{
			text += "+";
		}
		uint num2 = (uint)(text.Length - 1);
		foreach (Image body in m_BodyList)
		{
			if (num2 == 0)
			{
				body.gameObject.SetActive(value: false);
				continue;
			}
			num2--;
			body.gameObject.SetActive(value: true);
		}
		Number.text = text;
	}
}
