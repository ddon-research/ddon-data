using System.Collections.Generic;
using UnityEngine;

public class CustomMenuController : MonoBehaviour
{
	[SerializeField]
	private GameObject CustomMenuObject;

	private RectTransform CustomMenuTransform;

	private void Start()
	{
		CustomMenuTransform = CustomMenuObject.GetComponent<RectTransform>();
	}

	public CustomMenu CreateCustomMenu(Transform parent, List<CustomMenuContentData> data)
	{
		GameObject gameObject = Object.Instantiate(CustomMenuObject);
		gameObject.transform.parent = parent;
		gameObject.transform.localScale = new Vector3(1f, 1f, 1f);
		RectTransform component = gameObject.GetComponent<RectTransform>();
		CustomMenu component2 = gameObject.GetComponent<CustomMenu>();
		component.anchoredPosition = CustomMenuTransform.anchoredPosition;
		component2.SetContent(data);
		return component2;
	}
}
