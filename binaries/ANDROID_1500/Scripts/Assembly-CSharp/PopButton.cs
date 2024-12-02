using UnityEngine;

public class PopButton : MonoBehaviour
{
	public void OnClick()
	{
		SingletonMonoBehaviour<NavigationViewController>.Instance.Pop();
	}
}
