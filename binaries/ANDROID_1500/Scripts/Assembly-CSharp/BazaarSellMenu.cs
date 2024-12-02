using UnityEngine;

public class BazaarSellMenu : MonoBehaviour
{
	private void OnEnable()
	{
		SingletonMonoBehaviour<TutorialManager>.Instance.StartTutorial(TutorialManager.TutorialType.TUTORIAL_BAZAAR_SELL);
	}
}
