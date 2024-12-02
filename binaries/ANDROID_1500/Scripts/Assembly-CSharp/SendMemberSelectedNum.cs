using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(Text))]
public class SendMemberSelectedNum : MonoBehaviour
{
	private Text NumText;

	private void Start()
	{
		NumText = GetComponent<Text>();
	}

	private void Update()
	{
		NumText.text = SingletonMonoBehaviour<MailSendManager>.Instance.SelectedMemberList.Count.ToString();
	}
}
