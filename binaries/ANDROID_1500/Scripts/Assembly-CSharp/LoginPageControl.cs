using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class LoginPageControl : ViewController
{
	[SerializeField]
	private GameObject TitlePage;

	[SerializeField]
	private SelectCharacterViewController SelectCharacterView;

	[SerializeField]
	private InputField UserInput;

	[SerializeField]
	private InputField PassInput;

	[SerializeField]
	private Toggle SaveCOGIDToggle;

	public static LoginCharacterList CharacterList { get; private set; }

	private void Start()
	{
	}

	private void OnEnable()
	{
		string cogID = PlayerPerfManager.GetCogID();
		if (!(SaveCOGIDToggle == null))
		{
			if (!string.IsNullOrEmpty(cogID))
			{
				SaveCOGIDToggle.isOn = true;
				UserInput.text = cogID;
			}
			else
			{
				SaveCOGIDToggle.isOn = false;
				UserInput.text = string.Empty;
			}
		}
	}

	public void OnClickLogin()
	{
		if (string.IsNullOrEmpty(UserInput.text) || string.IsNullOrEmpty(PassInput.text))
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "ID,またはパスワードが未入力です");
			return;
		}
		if (SaveCOGIDToggle.isOn)
		{
			PlayerPerfManager.SetCogID(UserInput.text);
		}
		else
		{
			PlayerPerfManager.SetCogID(string.Empty);
		}
		COGCredential cOGCredential = new COGCredential();
		cOGCredential.ID = UserInput.text;
		cOGCredential.Password = PassInput.text;
		COGCredential credential = cOGCredential;
		StartCoroutine(CogAuth.Post(OnLogin, null, credential, LoadingAnimation.Default));
	}

	public void OnClickPrev()
	{
		base.CachedCanvasGroup.blocksRaycasts = false;
		base.CachedRectTransform.MoveTo(new Vector2(base.CachedRectTransform.anchoredPosition.x, 0f - base.CachedRectTransform.rect.height), 0.3f, 0f, iTween.EaseType.easeInCubic, delegate
		{
			base.gameObject.SetActive(value: false);
			base.CachedCanvasGroup.blocksRaycasts = true;
		});
	}

	public void OnClickFogetCredential()
	{
		Application.OpenURL("http://www.capcom-onlinegames.jp/pc/forgot");
	}

	public void OnLogin(LoginCharacterList characterList)
	{
		CharacterList = characterList;
		base.CachedCanvasGroup.blocksRaycasts = false;
		SelectCharacterView.OneTimeToken = characterList.Token;
		SelectCharacterView.SetCharacterList(characterList);
		SelectCharacterView.gameObject.SetActive(value: true);
		base.CachedRectTransform.MoveTo(new Vector2(base.CachedRectTransform.anchoredPosition.x, 0f - base.CachedRectTransform.rect.height), 0.3f, 0f, iTween.EaseType.easeInCubic, delegate
		{
			TitlePage.SetActive(value: false);
			base.gameObject.SetActive(value: false);
			base.CachedCanvasGroup.blocksRaycasts = true;
		});
	}
}
