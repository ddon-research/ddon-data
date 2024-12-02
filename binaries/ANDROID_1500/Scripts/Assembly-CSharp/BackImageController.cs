using System.Collections;
using UnityEngine;
using UnityEngine.UI;

public class BackImageController : MonoBehaviour
{
	private IEnumerator routine;

	private bool NeedReload;

	[SerializeField]
	private BackImageSelector BackSelector;

	private Image _MyImage;

	public Image MyImage
	{
		get
		{
			if (_MyImage == null)
			{
				_MyImage = GetComponent<Image>();
			}
			return _MyImage;
		}
		set
		{
			_MyImage = value;
		}
	}

	public void Init()
	{
		BackSelector.Init();
		MarkReload();
	}

	private void Reload()
	{
		string path = BackSelector.GetPath();
		LoadImageAsync(path);
	}

	private void Update()
	{
		if (NeedReload)
		{
			Reload();
			NeedReload = false;
		}
	}

	private void OnEnable()
	{
		if (routine != null)
		{
			StartCoroutine(routine);
		}
	}

	public void MarkReload()
	{
		NeedReload = true;
	}

	public void LoadImageAsync(string path)
	{
		MyImage.enabled = true;
		string filePath = "Images/calendar/bg_calendar/" + path;
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
