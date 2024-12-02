using System;
using UnityEngine;
using UnityEngine.UI;

public class NoticeBar : MonoBehaviour
{
	[SerializeField]
	private Text NoticeName;

	private Action onCallBack;

	public void UpdateContent(NoticeBarContent content)
	{
		NoticeName.text = content.Name;
		onCallBack = content.onCallback;
	}

	public void OnClick()
	{
		if (onCallBack != null)
		{
			onCallBack();
		}
	}
}
