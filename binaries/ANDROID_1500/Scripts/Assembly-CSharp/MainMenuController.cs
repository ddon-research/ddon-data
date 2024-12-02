using UnityEngine;

public class MainMenuController : ViewController
{
	private PagingScrollViewController PagingController;

	private void OnEnable()
	{
		SingletonMonoBehaviour<LoginBonusManager>.Instance.CheckLoginBonus();
	}

	public void Logout()
	{
		SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK_Cancel, "確認", "ログアウトしますか？", delegate(ModalDialog.Result result)
		{
			if (result == ModalDialog.Result.OK)
			{
				SingletonMonoBehaviour<FadeController>.Instance.FadeIn(delegate
				{
					WebAPIController.Instance.ClearApiToken();
					NavigationViewController.ResetScene();
				});
			}
		});
	}

	public void ToHelpPage()
	{
		Application.OpenURL("https://members.dd-on.jp/app/support/help.html");
	}

	public void ToSupportPage()
	{
		Application.OpenURL("https://members.dd-on.jp/form/app");
	}

	public void ToPolicyPage()
	{
		Application.OpenURL("https://members.dd-on.jp/app/support/rule.html");
	}

	public void ToOfficalPage()
	{
		Application.OpenURL("https://members.dd-on.jp/");
	}

	public void ToWebRestania()
	{
		Application.OpenURL("https://members.dd-on.jp/lestanianews/top");
	}
}
