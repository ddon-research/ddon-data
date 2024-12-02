using UnityEngine;
using UnityEngine.UI;

public class ServerUIElementSearchMonster : ServerUIElementBase
{
	[SerializeField]
	private InputField FirstFiled;

	[SerializeField]
	private InputField SecondFiled;

	public override void SetupElement()
	{
		SecondFiled.text = "1";
	}

	public override void OnPush()
	{
		if (FirstFiled.text == string.Empty)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "モンスター名を入力してください");
			return;
		}
		if (SecondFiled.text == string.Empty)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "モンスターのレベルを入力してください");
			return;
		}
		ServerParam.Text1 = FirstFiled.text;
		ServerParam.Text2 = SecondFiled.text;
		base.OnPush();
	}
}
