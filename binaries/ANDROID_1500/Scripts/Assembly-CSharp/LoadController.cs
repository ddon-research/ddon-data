using System;
using System.Collections;
using UnityEngine;

public class LoadController : SingletonMonoBehaviour<LoadController>
{
	public enum LOADING_ANIM_TYPE
	{
		DEFAULT,
		BACK_GROUND
	}

	[SerializeField]
	private GameObject LoadingImage;

	[SerializeField]
	private RectTransform Icon;

	[SerializeField]
	private RectTransform MiniIcon;

	private Vector3 OriginAngle;

	[SerializeField]
	private float Speed = 5f;

	[SerializeField]
	private float DummyWait = 2f;

	private int IconRefCount;

	private int MiniIconRefCount;

	public bool IsActive => LoadingImage.activeInHierarchy;

	private void Start()
	{
		OriginAngle = Icon.eulerAngles;
		NavigationViewController.AddProhibit(LoadingImage);
	}

	private void Update()
	{
		if (!(LoadingImage == null))
		{
			if (LoadingImage.activeInHierarchy)
			{
				Icon.eulerAngles += new Vector3(0f, 0f, Speed * Time.deltaTime);
			}
			if (MiniIcon.gameObject.activeInHierarchy)
			{
				MiniIcon.eulerAngles += new Vector3(0f, 0f, Speed * Time.deltaTime);
			}
		}
	}

	public void SetLoadActive(bool active, LOADING_ANIM_TYPE type = LOADING_ANIM_TYPE.DEFAULT)
	{
		switch (type)
		{
		case LOADING_ANIM_TYPE.DEFAULT:
			NavigationViewController.AddProhibit(LoadingImage);
			if (active)
			{
				if (IconRefCount == 0)
				{
					Icon.eulerAngles = OriginAngle;
					Icon.gameObject.SetActive(value: true);
					LoadingImage.SetActive(value: true);
				}
				IconRefCount++;
			}
			else
			{
				IconRefCount = Math.Max(0, IconRefCount - 1);
				if (IconRefCount == 0)
				{
					Icon.gameObject.SetActive(value: false);
					LoadingImage.SetActive(value: false);
				}
			}
			break;
		case LOADING_ANIM_TYPE.BACK_GROUND:
			if (active)
			{
				if (MiniIconRefCount == 0)
				{
					MiniIcon.eulerAngles = OriginAngle;
					MiniIcon.gameObject.SetActive(value: true);
				}
				MiniIconRefCount++;
			}
			else
			{
				MiniIconRefCount = Math.Max(0, MiniIconRefCount - 1);
				if (MiniIconRefCount == 0)
				{
					MiniIcon.gameObject.SetActive(value: false);
				}
			}
			break;
		}
	}

	public void SetDummyActive()
	{
		SetLoadActive(active: true);
		StartCoroutine(DelayMethod(DummyWait, delegate
		{
			LoadingImage.SetActive(value: false);
		}));
	}

	private IEnumerator DelayMethod(float delayTime, Action action)
	{
		yield return new WaitForSeconds(delayTime);
		action();
	}
}
