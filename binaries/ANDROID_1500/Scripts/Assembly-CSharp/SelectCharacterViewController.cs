using System.Collections;
using Packet;
using UnityEngine;
using WebRequest;

public class SelectCharacterViewController : ViewController
{
	private static SelectCharacterViewController instance;

	public string OneTimeToken;

	[SerializeField]
	private MainViewController MainPage;

	public static SelectCharacterViewController Instance
	{
		get
		{
			if (instance == null)
			{
				instance = (SelectCharacterViewController)Object.FindObjectOfType(typeof(SelectCharacterViewController));
				if (instance == null)
				{
					Debug.LogError(string.Concat(typeof(SelectCharacterViewController), "is nothing"));
				}
			}
			return instance;
		}
	}

	public LoginCharacterList CharacterList { get; private set; }

	protected void Awake()
	{
		CheckInstance();
	}

	protected bool CheckInstance()
	{
		if (this == Instance)
		{
			return true;
		}
		Object.Destroy(this);
		return false;
	}

	public void SetCharacterList(LoginCharacterList list)
	{
		CharacterList = list;
	}

	public void OnClickElement(Object element)
	{
		SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		GameObject gameObject = element as GameObject;
		CharacterListBoxElement component = gameObject.GetComponent<CharacterListBoxElement>();
		StartCoroutine(WebAPIController.RequestApiToken(component.CharacterID, OneTimeToken, delegate
		{
			StartCoroutine(MoveToMain());
		}));
	}

	public IEnumerator MoveToMain()
	{
		yield return CharacterData.GetBase(delegate(CharacterDataBase data)
		{
			SingletonMonoBehaviour<ProfileManager>.Instance.SetCharacterData(data);
			SingletonMonoBehaviour<ChargeManager>.Instance.SetJem(data.Jem);
			MainPage.SetFirstLoading();
			MainPage.gameObject.SetActive(value: true);
			MainPage.SetCharacterData(data);
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			base.CachedRectTransform.MoveTo(new Vector2(base.CachedRectTransform.anchoredPosition.x, 0f - base.CachedRectTransform.rect.height), 0.3f, 0f, iTween.EaseType.easeInCubic, delegate
			{
				base.gameObject.SetActive(value: false);
				base.CachedCanvasGroup.blocksRaycasts = true;
			});
		}, null);
	}
}
