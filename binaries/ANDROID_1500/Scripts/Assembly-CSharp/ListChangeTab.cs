using System;
using UnityEngine;
using UnityEngine.UI;

public class ListChangeTab : MonoBehaviour
{
	[SerializeField]
	private Button LeftButton;

	[SerializeField]
	private Image LeftActiveImage;

	[SerializeField]
	private Button RightButton;

	[SerializeField]
	private Image RightActiveImage;

	public void SetCallback(Action leftCallback, Action rightCallback)
	{
		LeftButton.onClick.RemoveAllListeners();
		RightButton.onClick.RemoveAllListeners();
		LeftButton.onClick.AddListener(delegate
		{
			leftCallback();
			ChangeState(IsLeft: true);
		});
		RightButton.onClick.AddListener(delegate
		{
			rightCallback();
			ChangeState(IsLeft: false);
		});
	}

	public void ChangeState(bool IsLeft)
	{
		LeftActiveImage.gameObject.SetActive(value: false);
		RightActiveImage.gameObject.SetActive(value: false);
		if (IsLeft)
		{
			LeftActiveImage.gameObject.SetActive(value: true);
		}
		else
		{
			RightActiveImage.gameObject.SetActive(value: true);
		}
	}

	public void ChangeLeft()
	{
		LeftButton.onClick.Invoke();
	}

	public void ChangeRight()
	{
		RightButton.onClick.Invoke();
	}
}
