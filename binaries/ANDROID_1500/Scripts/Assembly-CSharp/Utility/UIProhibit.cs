using UnityEngine;

namespace Utility;

public class UIProhibit : MonoBehaviour
{
	public void OnEnable()
	{
		NavigationViewController.AddProhibit(base.gameObject);
	}
}
