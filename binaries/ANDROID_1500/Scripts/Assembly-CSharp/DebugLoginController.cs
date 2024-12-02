using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class DebugLoginController : MonoBehaviour
{
	[SerializeField]
	private LoginPageControl LoginPage;

	[SerializeField]
	private InputField UserNameInput;

	[SerializeField]
	private InputField CharacterIdInput;

	[SerializeField]
	private InputField COGIDInput;

	[SerializeField]
	private InputField COGPassInput;

	[SerializeField]
	private InputField LocalIPInput;

	private void Login()
	{
		bool flag = !string.IsNullOrEmpty(UserNameInput.text);
		bool flag2 = !string.IsNullOrEmpty(CharacterIdInput.text);
		bool flag3 = !string.IsNullOrEmpty(COGIDInput.text);
		if (flag)
		{
			StartCoroutine(Uraguchi.Post(LoginPage.OnLogin, null, UserNameInput.text, LoadingAnimation.Default));
		}
		else if (flag2)
		{
			StartCoroutine(Uraguchi.PostWithCharacterID(LoginPage.OnLogin, null, uint.Parse(CharacterIdInput.text), LoadingAnimation.Default));
		}
		else if (flag3)
		{
			COGCredential cOGCredential = new COGCredential();
			cOGCredential.ID = COGIDInput.text;
			cOGCredential.Password = COGPassInput.text;
			COGCredential credential = cOGCredential;
			StartCoroutine(CogAuth.Post(LoginPage.OnLogin, null, credential, LoadingAnimation.Default));
		}
		else
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "エラー", "名前かIDを入力してください");
		}
	}

	public void OnClickLogin()
	{
		WebAPIController.Instance.SetHost("http://172.31.23.55:58946");
		Login();
	}

	public void OnClickLocalLogin()
	{
		WebAPIController.Instance.SetHost("localhost:58946");
		if (!string.IsNullOrEmpty(LocalIPInput.text))
		{
			WebAPIController.Instance.SetHost("http://" + LocalIPInput.text + ":58946");
		}
		Login();
	}

	public void OnClickCloudLogin()
	{
		WebAPIController.Instance.SetHost("https://debug-companion.dd-on.net");
		Login();
	}

	public void OnClickCloudLogin2()
	{
		WebAPIController.Instance.SetHost("https://debug2-companion.dd-on.net:2443");
		Login();
	}

	public void OnClickCloudLogin3()
	{
		WebAPIController.Instance.SetHost("https://debug3-companion.dd-on.net:4443");
		Login();
	}

	public void OnClickStressLogin()
	{
		WebAPIController.Instance.SetHost("https://stage-companion.dd-on.net");
		Login();
	}

	public void OnClickStageLogin()
	{
		WebAPIController.Instance.SetHost("https://stage2-companion.dd-on.net");
		Login();
	}
}
