using UnityEngine;

public class BlackFadeController : MonoBehaviour
{
	public void CloseBlackout()
	{
		CanvasGroup component = GetComponent<CanvasGroup>();
		component.FadeTo(0f, SingletonMonoBehaviour<AppUtility>.Instance.FadeTime, 0f, iTween.EaseType.easeOutSine, delegate
		{
			Object.Destroy(base.gameObject);
		});
	}
}
