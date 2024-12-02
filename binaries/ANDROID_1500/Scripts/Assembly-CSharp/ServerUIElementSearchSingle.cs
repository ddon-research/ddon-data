using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementSearchSingle : ServerUIElementBase
{
	[SerializeField]
	private Text Label;

	[SerializeField]
	private InputField Filed;

	public override void SetupElement()
	{
		Label.text = DispParam.Text1;
	}

	public override void OnPush()
	{
		if (Filed.text == string.Empty)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", DispParam.Text1 + "を入力してください");
			return;
		}
		ServerParam.Text1 = Filed.text;
		base.OnPush();
	}
}
