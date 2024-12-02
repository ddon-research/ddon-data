using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementTableContent : ServerUIElementBase
{
	[SerializeField]
	private Text Label1;

	[SerializeField]
	private Text Label2;

	[SerializeField]
	private GameObject Header1;

	[SerializeField]
	private GameObject Header2;

	public override void SetupElement()
	{
		Header1.SetActive(value: false);
		Header2.SetActive(value: false);
		Label1.text = DispParam.Text1;
		if (Label1.text.Length > 0)
		{
			Header1.SetActive(value: true);
		}
		Label2.text = DispParam.Text2;
		if (Label2.text.Length > 0)
		{
			Header2.SetActive(value: true);
		}
	}
}
