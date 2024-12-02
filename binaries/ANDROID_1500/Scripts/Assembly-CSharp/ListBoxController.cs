using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(ContentSizeFitter))]
[RequireComponent(typeof(VerticalLayoutGroup))]
public abstract class ListBoxController<T> : ViewController
{
	public List<T> DataSources = new List<T>();

	[SerializeField]
	private GameObject ElementBase;

	private List<ListBoxElement<T>> Elements = new List<ListBoxElement<T>>();

	private void Awake()
	{
		ElementBase.SetActive(value: false);
	}

	private void OnEnable()
	{
		DataSources.Clear();
		Setup(DataSources);
	}

	protected abstract void Setup(List<T> dataSources);

	public void Clear()
	{
		DataSources.Clear();
		foreach (ListBoxElement<T> element in Elements)
		{
			Object.Destroy(element.gameObject);
		}
		Elements.Clear();
	}

	public void CreateElements()
	{
		foreach (ListBoxElement<T> element in Elements)
		{
			Object.Destroy(element.gameObject);
		}
		Elements.Clear();
		foreach (T dataSource in DataSources)
		{
			GameObject gameObject = Object.Instantiate(ElementBase);
			gameObject.SetActive(value: true);
			ListBoxElement<T> component = gameObject.GetComponent<ListBoxElement<T>>();
			Vector3 localScale = component.transform.localScale;
			Vector2 sizeDelta = component.CachedRectTransform.sizeDelta;
			Vector2 offsetMin = component.CachedRectTransform.offsetMin;
			Vector2 offsetMax = component.CachedRectTransform.offsetMax;
			component.transform.SetParent(ElementBase.transform.parent);
			component.transform.localScale = localScale;
			component.CachedRectTransform.sizeDelta = sizeDelta;
			component.CachedRectTransform.offsetMin = offsetMin;
			component.CachedRectTransform.offsetMax = offsetMax;
			component.UpdateContent(dataSource);
			Elements.Add(component);
		}
	}
}
