using System.Collections;
using UnityEngine;
using UnityEngine.UI;

public class BackImageItem : MonoBehaviour
{
	[SerializeField]
	private GameObject Selector;

	[SerializeField]
	private BackImageSelector _SelectorController;

	private IEnumerator routine;

	[SerializeField]
	private Image MyImage;

	private BackImageSelector SelectorController
	{
		get
		{
			if (_SelectorController == null)
			{
				_SelectorController = base.transform.parent.GetComponent<BackImageSelector>();
			}
			return _SelectorController;
		}
		set
		{
			_SelectorController = value;
		}
	}

	public int BackImageIndex { get; private set; }

	public bool IsSelected => Selector.activeSelf;

	public void Select(bool flag)
	{
		Selector.SetActive(flag);
	}

	private void OnEnable()
	{
		if (routine != null)
		{
			StartCoroutine(routine);
		}
	}

	public void OnClick()
	{
		SelectorController.AllOff();
		Select(flag: true);
	}

	public void UpdateContent(int index, string thumbPath)
	{
		BackImageIndex = index;
		LoadImageAsync(thumbPath);
	}

	public void LoadImageAsync(string path)
	{
		MyImage.enabled = true;
		string filePath = "Images/calendar/bg_calendarthumb/" + path;
		routine = LoadManager.LoadAsync(filePath, delegate(Sprite res)
		{
			if (MyImage != null)
			{
				MyImage.sprite = res;
			}
		});
		if (base.gameObject.activeInHierarchy)
		{
			StartCoroutine(routine);
		}
	}
}
