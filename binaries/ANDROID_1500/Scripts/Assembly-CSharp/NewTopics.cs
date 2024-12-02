using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class NewTopics : MonoBehaviour
{
	[SerializeField]
	private Text NumText;

	[SerializeField]
	protected Text NewNum;

	[SerializeField]
	private Image Left;

	[SerializeField]
	private Image Right;

	[SerializeField]
	private Image Body;

	[SerializeField]
	protected uint MaxNum = 99u;

	protected List<Image> m_BodyList = new List<Image>();

	private void Awake()
	{
		m_BodyList.Add(Body);
		Body.gameObject.SetActive(value: false);
		uint num = MaxNum;
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

	public void UpdateContent(uint num, uint max, uint newNum, bool isDisplayMax = true)
	{
		if (NumText != null)
		{
			if (isDisplayMax)
			{
				NumText.text = num + "/" + max;
			}
			else
			{
				NumText.text = num.ToString();
			}
		}
		GameObject gameObject = NewNum.gameObject.transform.parent.gameObject;
		if (newNum == 0)
		{
			gameObject.SetActive(value: false);
			return;
		}
		string text = newNum.ToString();
		if (newNum >= MaxNum)
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
		NewNum.text = text;
		gameObject.SetActive(value: true);
	}
}
