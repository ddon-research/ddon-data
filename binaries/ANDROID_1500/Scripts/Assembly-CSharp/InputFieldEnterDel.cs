using UnityEngine.UI;

public class InputFieldEnterDel : InputField
{
	public string textEnterDel
	{
		get
		{
			EnterDel(base.text);
			return base.text;
		}
	}

	protected override void Start()
	{
		base.Start();
		base.onEndEdit.AddListener(EnterDel);
	}

	private void EnterDel(string str)
	{
		base.text = str.Replace("\r", string.Empty).Replace("\n", string.Empty);
	}
}
