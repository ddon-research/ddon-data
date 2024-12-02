using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

public class InputForm : MonoBehaviour
{
	[SerializeField]
	private GameObject BackButtonObject;

	[SerializeField]
	private GameObject DummyInput;

	[SerializeField]
	private Text DummyInputText;

	[SerializeField]
	private GameObject InputScroll;

	[SerializeField]
	private InputField InputField;

	[SerializeField]
	private RectTransform InputContent;

	[SerializeField]
	private Button InputButton;

	[SerializeField]
	private RectTransform InputHolder;

	[SerializeField]
	protected Vector2 BodyOriginzSize = Vector2.zero;

	[SerializeField]
	protected Vector2 BodyOriginPos = Vector2.zero;

	[SerializeField]
	public bool IsActive => InputScroll.activeInHierarchy;

	private void Awake()
	{
		NavigationViewController.AddProhibit(InputScroll);
	}

	private void Start()
	{
		OnDeactivate();
	}

	protected void ResetFields()
	{
		if (BodyOriginzSize == Vector2.zero)
		{
			BodyOriginzSize = InputHolder.sizeDelta;
			BodyOriginPos = InputContent.localPosition;
		}
		InputContent.localPosition = BodyOriginPos;
		InputHolder.sizeDelta = BodyOriginzSize;
	}

	public void OnActivate()
	{
		ResetFields();
		DummyInput.SetActive(value: false);
		BackButtonObject.SetActive(value: true);
		InputScroll.SetActive(value: true);
		EventSystem.current.SetSelectedGameObject(InputField.gameObject, null);
		InputField.OnPointerClick(new PointerEventData(EventSystem.current));
	}

	public void OnDeactivate()
	{
		DummyInputText.text = InputField.text;
		DummyInput.SetActive(value: true);
		BackButtonObject.SetActive(value: false);
		InputScroll.SetActive(value: false);
	}

	public void ScrollDown()
	{
		InputContent.position = new Vector2(InputContent.position.x, 0f);
	}
}
