using Frame;
using Packet;
using UnityEngine;
using UnityEngine.EventSystems;
using WebRequest;

public class MainViewController : ViewController
{
	private static MainViewController instance;

	private EventSystem EventSystem;

	private CharacterDataBase CharacterData;

	public bool IsFirstLoading;

	[SerializeField]
	private TopFrameController TopFrame;

	[SerializeField]
	private HomeController Home;

	public static MainViewController Instance
	{
		get
		{
			if (instance == null)
			{
				instance = (MainViewController)Object.FindObjectOfType(typeof(MainViewController));
				if (instance == null)
				{
					Debug.LogError(string.Concat(typeof(MainViewController), "is nothing"));
				}
			}
			return instance;
		}
	}

	protected void Awake()
	{
		EventSystem = Object.FindObjectOfType<EventSystem>();
		CheckInstance();
		StartCoroutine(InGameURL.GetStaticResource(delegate(string url)
		{
			ImageDownloader.CDNHost = url;
		}, null));
		SingletonMonoBehaviour<TutorialManager>.Instance.LoadTutorialData();
	}

	private void OnEnable()
	{
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

	public void SetCharacterGold(uint gold)
	{
		CharacterData.Gold = gold;
		TopFrame.SetGold(gold);
	}

	public void SetFirstLoading()
	{
		if (EventSystem == null)
		{
			EventSystem = Object.FindObjectOfType<EventSystem>();
		}
		IsFirstLoading = true;
		EventSystem.enabled = false;
	}

	private void Update()
	{
		if (IsFirstLoading && !SingletonMonoBehaviour<TutorialManager>.Instance.IsLoading)
		{
			EventSystem.enabled = true;
			IsFirstLoading = false;
			SingletonMonoBehaviour<TutorialManager>.Instance.StartTutorial(TutorialManager.TutorialType.TUTORIAL_MAIN);
		}
	}

	public void SetCharacterData(CharacterDataBase data)
	{
		CharacterData = data;
		TopFrame.UpdateContent(data);
	}

	public void UpdateIcon(uint id)
	{
		CharacterData.IconID = id;
		TopFrame.UpdateIcon(id);
	}
}
