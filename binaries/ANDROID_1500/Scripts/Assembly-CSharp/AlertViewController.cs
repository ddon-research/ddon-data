using System;
using UnityEngine;
using UnityEngine.UI;

public class AlertViewController : ViewController
{
	[SerializeField]
	private Text titleLabel;

	[SerializeField]
	private Text messageLabel;

	[SerializeField]
	private Button cancelButton;

	[SerializeField]
	private Text cancelButtonLabel;

	[SerializeField]
	private Button okButton;

	[SerializeField]
	private Text okButtonLabel;

	private static GameObject prefab;

	private Action cancelButtonDelegate;

	private Action okButtonDelegate;

	public static AlertViewController Show(string title, string message, AlertViewOptions options = null)
	{
		if (prefab == null)
		{
			prefab = Resources.Load("Alert View") as GameObject;
		}
		GameObject gameObject = UnityEngine.Object.Instantiate(prefab);
		AlertViewController component = gameObject.GetComponent<AlertViewController>();
		component.UpdateContent(title, message, options);
		return component;
	}

	public void UpdateContent(string title, string message, AlertViewOptions options = null)
	{
		titleLabel.text = title;
		messageLabel.text = message;
		if (options != null)
		{
			cancelButton.transform.parent.gameObject.SetActive(options.cancelButtonTitle != null || options.okButtonTitle != null);
			cancelButton.gameObject.SetActive(options.cancelButtonTitle != null);
			cancelButtonLabel.text = options.cancelButtonTitle ?? string.Empty;
			cancelButtonDelegate = options.cancelButtonDelegate;
			okButton.gameObject.SetActive(options.okButtonTitle != null);
			okButtonLabel.text = options.okButtonTitle ?? string.Empty;
			okButtonDelegate = options.okButtonDelegate;
		}
		else
		{
			cancelButton.gameObject.SetActive(value: false);
			okButton.gameObject.SetActive(value: true);
			okButtonLabel.text = "OK";
		}
	}

	public void Dismiss()
	{
		UnityEngine.Object.Destroy(base.gameObject);
	}

	public void OnPressCancelButton()
	{
		if (cancelButtonDelegate != null)
		{
			cancelButtonDelegate();
		}
		Dismiss();
	}

	public void OnPressOKButton()
	{
		if (okButtonDelegate != null)
		{
			okButtonDelegate();
		}
		Dismiss();
	}
}
