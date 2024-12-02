using UnityEngine;

[RequireComponent(typeof(ViewController))]
public class CalendarInit : MonoBehaviour
{
	public NavigationViewController m_NavigationViewController;

	private void Start()
	{
		ViewController component = GetComponent<ViewController>();
		m_NavigationViewController.Push(component);
	}
}
