using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(CanvasGroup))]
public class ButtomDialogController : ViewController
{
	public static ButtomDialogController Singleton;

	[SerializeField]
	private GameObject ElementBase;

	[SerializeField]
	private Text DialogText;

	private List<ButtomDialogElement> Elements = new List<ButtomDialogElement>();

	public ButtomDialogController()
	{
		if (Singleton == null)
		{
			Singleton = this;
		}
	}

	private void Start()
	{
		ElementBase.SetActive(value: false);
	}

	public static GameObject CreateDialog(Transform parent, List<ButtomDialogData> datas)
	{
		GameObject gameObject = Object.Instantiate(Singleton.gameObject);
		gameObject.SetActive(value: true);
		ButtomDialogController control = gameObject.GetComponent<ButtomDialogController>();
		SetParent(control, parent);
		foreach (ButtomDialogData data in datas)
		{
			GameObject gameObject2 = Object.Instantiate(control.ElementBase);
			gameObject2.SetActive(value: true);
			ButtomDialogElement component = gameObject2.GetComponent<ButtomDialogElement>();
			SetParent(component, control.ElementBase.transform.parent);
			component.UpdateContent(control, data);
			control.Elements.Add(component);
		}
		control.CachedCanvasGroup.blocksRaycasts = false;
		Vector2 anchoredPosition = control.CachedRectTransform.anchoredPosition;
		control.CachedRectTransform.anchoredPosition = new Vector2(control.CachedRectTransform.anchoredPosition.x, 0f - control.CachedRectTransform.rect.height);
		control.CachedRectTransform.MoveTo(anchoredPosition, 0.2f, 0f, iTween.EaseType.easeInSine, delegate
		{
			control.CachedCanvasGroup.blocksRaycasts = true;
		});
		return gameObject;
	}

	public static void CloseDialog(GameObject dialog)
	{
		ButtomDialogController component = dialog.GetComponent<ButtomDialogController>();
		component.CachedCanvasGroup.blocksRaycasts = false;
		Vector2 pos = new Vector2(component.CachedRectTransform.anchoredPosition.x, 0f - component.CachedRectTransform.rect.height);
		component.CachedRectTransform.MoveTo(pos, 0.2f, 0f, iTween.EaseType.easeInSine, delegate
		{
			Object.Destroy(dialog);
		});
	}

	private static void SetParent(ViewController elem, Transform parent)
	{
		Vector3 localScale = elem.transform.localScale;
		Vector2 sizeDelta = elem.CachedRectTransform.sizeDelta;
		Vector2 offsetMin = elem.CachedRectTransform.offsetMin;
		Vector2 offsetMax = elem.CachedRectTransform.offsetMax;
		elem.transform.SetParent(parent);
		elem.transform.localScale = localScale;
		elem.CachedRectTransform.sizeDelta = sizeDelta;
		elem.CachedRectTransform.offsetMin = offsetMin;
		elem.CachedRectTransform.offsetMax = offsetMax;
	}
}
