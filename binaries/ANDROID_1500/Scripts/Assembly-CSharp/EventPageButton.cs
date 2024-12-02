using UnityEngine;

public class EventPageButton : MonoBehaviour
{
	[SerializeField]
	private GameObject NewEffect;

	private void Update()
	{
		bool flag = SingletonMonoBehaviour<ProfileManager>.Instance.CheckNewEvent();
		if (!NewEffect.activeSelf && flag)
		{
			NewEffect.SetActive(value: true);
		}
		else if (NewEffect.activeSelf && !flag)
		{
			NewEffect.SetActive(value: false);
		}
	}

	public void OnPush()
	{
		SingletonMonoBehaviour<ProfileManager>.Instance.UpdateEventLastCheckTime();
	}
}
