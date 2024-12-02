using System;
using Packet;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.Events;
using UnityEngine.Networking;
using UnityEngine.UI;
using WebRequest;

public class ClanTopicDetail : TopicDetail
{
	[SerializeField]
	private ClanTopicBase TopicBase;

	[SerializeField]
	public GameObject m_MainTabButtonImage;

	[SerializeField]
	public GameObject m_CommentTabButtonImage;

	[SerializeField]
	public GameObject m_CommentScrollView;

	[SerializeField]
	public CommentListViewer m_CommentListViewer;

	[SerializeField]
	public GameObject m_MainScrollView;

	[SerializeField]
	public GameObject m_MainScrollContent;

	[SerializeField]
	public GameObject m_MainScrollTopicBase;

	[SerializeField]
	private InputField m_InputField;

	[SerializeField]
	private GameObject m_InputText;

	[SerializeField]
	private Text m_InputDummy;

	[SerializeField]
	private GameObject m_CommentControls;

	[SerializeField]
	private GameObject m_MainControls;

	[SerializeField]
	private bool IsInitActiveCommentTab;

	[SerializeField]
	private GameObject DefiniteDateLabel;

	[SerializeField]
	private GameObject InDefiniteDateLabel;

	[SerializeField]
	protected bool IsPosting;

	protected object thisLock = new object();

	public new void Start()
	{
		if (!IsInitActiveCommentTab)
		{
			OnChangeMainView();
		}
		base.Start();
	}

	private new void Update()
	{
		base.Update();
	}

	public override void UpdateContent(CalendarTopic topic)
	{
		Type = topic.Type;
		InitControl(topic);
		BaseScrollbar.value = 1f;
		TopicData = topic;
		MyCanvasGroup.alpha = 1f;
		m_TopicId = topic.TopicId;
		m_CalendarId = topic.CalendarId;
		ReadTopic();
		if (topic.Content.Length > 0)
		{
			TopicBase.UpdateContent(topic);
			MyImageGrid.UpdateContent(topic.ImageInfoList);
		}
		else
		{
			MyCanvasGroup.alpha = 0f;
		}
		TopicTitle.text = topic.Title;
		DateTime dateTime = DateTime.Parse(topic.BeginDate);
		DateTime dateTime2 = DateTime.Parse(topic.EndDate);
		DateTime lastUpdate = DateTime.Parse(topic.ModifiedAt);
		LastUpdate = lastUpdate;
		BeginDate.text = dateTime.ToString("yyyy.MM.dd HH:mm");
		EndDate.text = dateTime2.ToString("yyyy.MM.dd HH:mm");
		DefiniteDateLabel.SetActive(value: false);
		InDefiniteDateLabel.SetActive(value: false);
		if ("1900-01-01T00:00:00+09:00" == topic.BeginDate && "2100-01-01T00:00:00+09:00" == topic.EndDate)
		{
			InDefiniteDateLabel.SetActive(value: true);
		}
		else
		{
			DefiniteDateLabel.SetActive(value: true);
		}
		m_CommentListViewer.InitContent(topic, 0u);
		base.MyRebuilder.MarkRebuild();
		RectTransform component = m_MainScrollContent.GetComponent<RectTransform>();
		component.localPosition = new Vector3(component.localPosition.x, 0f, component.localPosition.z);
		m_LikeButton.UpdateContent(topic.IsLiked, topic.LikeNum, Type);
		MyReloadChecker.Init(delegate
		{
			CharacterCalendar.ClearCache();
			ReloadContent();
		});
	}

	public void OnChangeMainView()
	{
		m_MainTabButtonImage.SetActive(value: true);
		m_CommentTabButtonImage.SetActive(value: false);
		m_MainScrollView.SetActive(value: true);
		m_CommentScrollView.SetActive(value: false);
		m_CommentControls.SetActive(value: false);
		m_MainControls.SetActive(value: true);
		if (customMenu != null)
		{
			bool flag = customMenu.IsMenuEmpty();
			customMenu.gameObject.SetActive(!flag);
		}
		if (EventSystem.current != null)
		{
			EventSystem.current.SetSelectedGameObject(null);
		}
		StartCoroutine(UpdateCheck());
	}

	public void OnChangeCommentView()
	{
		m_CommentTabButtonImage.SetActive(value: true);
		m_MainTabButtonImage.SetActive(value: false);
		m_CommentScrollView.SetActive(value: true);
		m_MainScrollView.SetActive(value: false);
		if (m_CommentListViewer.gameObject.activeInHierarchy)
		{
			m_CommentListViewer.LoadContent();
		}
		m_CommentControls.SetActive(value: true);
		m_MainControls.SetActive(value: false);
		if (customMenu != null)
		{
			bool flag = customMenu.IsMenuEmpty();
			customMenu.gameObject.SetActive(!flag);
		}
		if (EventSystem.current != null)
		{
			EventSystem.current.SetSelectedGameObject(null);
		}
	}

	public override void OnNavigationPushEnd()
	{
		base.OnNavigationPushEnd();
		SelectDefaultTab();
		IsPosting = false;
	}

	public void SelectDefaultTab()
	{
		if (Type == CalendarTopic.CALENDAR_TYPE.CLAN)
		{
			OnChangeMainView();
		}
		else if (Type == CalendarTopic.CALENDAR_TYPE.CLAN_MESSAGE_BOARD)
		{
			OnChangeCommentView();
		}
	}

	public override void OnNavigationPopBegin()
	{
		m_CommentListViewer.OnNavigationPopBegin();
		ResetInputForm();
		OnChangeMainView();
		base.OnNavigationPopBegin();
		m_CommentListViewer.DestroyCommentImage();
	}

	public bool CheckData(TopicComment com, bool isEdit = false)
	{
		if (com.Content.Length == 0)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "投稿エラー", "コメントを入力してください。");
			return false;
		}
		if (com.Content.Length > 150)
		{
			Debug.Log("投稿エラー：コメントは150文字以内に収めてください。");
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "投稿エラー", "コメントが最大文字数を超えています。\n150文字以下にしてください。\n(現在：" + com.Content.Length + "文字)");
			return false;
		}
		if (m_CommentListViewer.CommentCounter >= m_CommentListViewer.CommentMaxLimit && TopicData.Type == CalendarTopic.CALENDAR_TYPE.CLAN && !isEdit)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "投稿エラー", "コメント数が" + m_CommentListViewer.CommentMaxLimit + "件を超えました。\n新しいトピックを作成してください。");
			return false;
		}
		return true;
	}

	public void SendResComment()
	{
		TopicComment topicComment = new TopicComment();
		topicComment.CalendarId = m_CalendarId;
		topicComment.TopicId = m_TopicId;
		topicComment.Content = m_InputField.text;
		if (!CheckData(topicComment))
		{
			Debug.Log("投稿時チェックに失敗");
			return;
		}
		lock (thisLock)
		{
			if (IsPosting)
			{
				return;
			}
			IsPosting = true;
		}
		StartCoroutine(CharacterCalendar.PostComment(delegate
		{
			CharacterCalendar.ClearCache_GetCommentUInt64UInt32();
			m_CommentListViewer.UpdatePageJumpComments(0, IsForce: true);
			SingletonMonoBehaviour<CalendarManager>.Instance.TypedTopicListView.MarkReload();
			IsPosting = false;
		}, delegate(UnityWebRequest result)
		{
			AppUtility.ShowErr(result.downloadHandler.text, "TopicComment", IsPop: false);
			IsPosting = false;
		}, "comment", topicComment, LoadingAnimation.Default));
		ResetInputForm();
	}

	public void ResetInputForm()
	{
		m_InputField.text = string.Empty;
		m_InputDummy.text = string.Empty;
	}

	public void ActivateCommentForm()
	{
		m_InputField.ActivateInputField();
		UnityEvent unityEvent = new UnityEvent();
		unityEvent.Invoke();
	}
}
