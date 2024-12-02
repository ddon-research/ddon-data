using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(InputField))]
public class TextNum : MonoBehaviour
{
	[SerializeField]
	private InputField Text;

	[SerializeField]
	private uint MaxTextNum;

	private Text m_NumText;

	private uint m_Num;

	private void Start()
	{
		m_NumText = GetComponent<Text>();
		m_NumText.text = "0 / " + MaxTextNum;
	}

	private void Update()
	{
		if (!(m_NumText == null) && !(Text == null))
		{
			uint num = (uint)Text.text.Length;
			if (num > MaxTextNum)
			{
				num = MaxTextNum;
			}
			if (num != m_Num)
			{
				m_NumText.text = num + " / " + MaxTextNum;
				m_Num = num;
			}
		}
	}
}
