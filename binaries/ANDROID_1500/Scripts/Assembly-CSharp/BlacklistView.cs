public class BlacklistView : ViewController
{
	private void Start()
	{
		base.PopBeginCheckMessage = "ブラックリストの編集を終了しますか？\n（操作内容は保存されません）";
	}

	public override void OnNavigationPushEnd()
	{
		base.IsPopBeginCheck = false;
	}

	public override void OnNavigationPopBegin()
	{
	}
}
