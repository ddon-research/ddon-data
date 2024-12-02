using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(GridLayoutGroup))]
public class ImageNumber : MonoBehaviour
{
	[SerializeField]
	private Image Number;

	[SerializeField]
	private Sprite[] NumberSprite;

	[SerializeField]
	private uint MaxNumber = 9999u;

	[SerializeField]
	private uint Value;

	private List<Image> m_NumberList = new List<Image>();

	private void Start()
	{
		if (Number == null || NumberSprite == null)
		{
			return;
		}
		m_NumberList.Add(Number);
		uint num = 1u;
		uint num2 = MaxNumber;
		while (num2 != 0)
		{
			num2 /= 10;
			if (num2 == 0)
			{
				break;
			}
			num++;
		}
		for (int i = m_NumberList.Count; i < num; i++)
		{
			Image image = Object.Instantiate(Number);
			image.rectTransform.SetParent(Number.transform.parent.transform, worldPositionStays: false);
			image.sprite = NumberSprite[0];
			image.gameObject.SetActive(value: false);
			m_NumberList.Add(image);
		}
		SetNumber(Value);
	}

	public void SetNumber(uint num)
	{
		if (num > MaxNumber)
		{
			num = MaxNumber;
		}
		for (int num2 = m_NumberList.Count - 1; num2 >= 0; num2--)
		{
			if (num == 0 && num2 != m_NumberList.Count - 1)
			{
				m_NumberList[num2].gameObject.SetActive(value: false);
			}
			else
			{
				m_NumberList[num2].gameObject.SetActive(value: true);
				uint num3 = num % 10;
				num /= 10;
				m_NumberList[num2].sprite = NumberSprite[num3];
			}
		}
	}
}
