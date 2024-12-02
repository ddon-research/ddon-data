using System.Collections;
using UnityEngine;
using UnityEngine.EventSystems;

public abstract class ViewControllerAfterLoad : ViewController
{
	protected class ReqestResult
	{
		public bool isError;

		public bool isErrorDefaultDialog = true;
	}

	private Vector2 _pos;

	protected abstract IEnumerator LoadRoutine(ReqestResult result);

	public new void Push()
	{
		RectTransform component = GetComponent<RectTransform>();
		_pos = component.anchoredPosition;
		component.anchoredPosition += component.rect.size;
		base.gameObject.SetActive(value: true);
		Object.FindObjectOfType<EventSystem>().enabled = false;
		StartCoroutine(_LoadRoutine());
	}

	private IEnumerator _LoadRoutine()
	{
		ReqestResult result = new ReqestResult();
		yield return LoadRoutine(result);
		RectTransform t = GetComponent<RectTransform>();
		t.anchoredPosition = _pos;
		if (result.isError)
		{
			base.gameObject.SetActive(value: false);
			Object.FindObjectOfType<EventSystem>().enabled = true;
			if (result.isErrorDefaultDialog)
			{
				SingletonMonoBehaviour<ModalDialog>.Instance.Error(ModalDialog.Mode.OK, "サーバーエラー", "リクエストに失敗しました。");
			}
		}
		else
		{
			SingletonMonoBehaviour<NavigationViewController>.Instance.Push(this);
		}
		yield return null;
	}
}
