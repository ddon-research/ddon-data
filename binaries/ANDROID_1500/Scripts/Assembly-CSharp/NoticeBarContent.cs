using System;

public class NoticeBarContent
{
	private string _Name;

	private Action _onCallback;

	public string Name
	{
		get
		{
			return _Name;
		}
		private set
		{
			_Name = value;
		}
	}

	public Action onCallback
	{
		get
		{
			return _onCallback;
		}
		private set
		{
			_onCallback = value;
		}
	}

	public NoticeBarContent(string name, Action callback = null)
	{
		Name = name;
		onCallback = callback;
	}
}
