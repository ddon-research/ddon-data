using Packet;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Networking;
using UnityEngine.UI;
using WebRequest;

public class EditComment : MonoBehaviour
{
	public enum CommentEditType
	{
		EDIT = 1,
		SELECT
	}

	[SerializeField]
	private InputField Content;

	[SerializeField]
	private CanvasGroup Background;

	[SerializeField]
	private float FadeAnimTime;

	[SerializeField]
	private bool IsAnimating;

	[SerializeField]
	private TopicComment CommentData;

	[SerializeField]
	private CommentListViewer MyCommentList;

	[SerializeField]
	protected Scrollbar BaseScrollbar;

	[SerializeField]
	protected RectTransform ContentTrans;

	[SerializeField]
	protected Vector3 BodyOriginTrans = Vector3.zero;

	[SerializeField]
	protected Text MyText;

	[SerializeField]
	protected ChildTextFitter MyChildTextFitter;

	[SerializeField]
	protected RectTransform InputForm;

	[SerializeField]
	protected AutoLayoutRebuilder MyRebuilder;

	[SerializeField]
	protected Button InputButton;

	[SerializeField]
	protected bool IsPosting;

	protected object thisLock = new object();

	[SerializeField]
	protected Text Title;

	[SerializeField]
	protected GameObject EditControl;

	[SerializeField]
	protected GameObject SelectControl;

	private void Awake()
	{
		NavigationViewController.AddProhibit(Background.gameObject);
	}

	public void PostData()
	{
		if (IsAnimating)
		{
			return;
		}
		CommentData.Content = Content.text;
		if (!SingletonMonoBehaviour<CalendarManager>.Instance.ClanTopicDetail.CheckData(CommentData, isEdit: true))
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
		StartCoroutine(CharacterCalendar.PutComment(delegate
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "完了確認", "コメントを編集しました。", delegate(ModalDialog.Result res)
			{
				if (res == ModalDialog.Result.OK)
				{
					CharacterCalendar.ClearCache_GetCommentUInt64UInt32();
					MyCommentList.Reload(NeedTopicListReload: true);
					IsPosting = false;
				}
			});
			OnDeactivate();
		}, delegate(UnityWebRequest result)
		{
			AppUtility.ShowErr(result.downloadHandler.text, "TopicComment", IsPop: false);
			IsPosting = false;
		}, CommentData, LoadingAnimation.Default));
	}

	protected void RestFields()
	{
		ContentTrans.anchoredPosition = new Vector2(ContentTrans.anchoredPosition.x, 0f);
		RectTransform component = Content.gameObject.GetComponent<RectTransform>();
		InputForm.sizeDelta = BodyOriginTrans;
		component.sizeDelta = BodyOriginTrans;
	}

	private void SetupControl(CommentEditType type)
	{
		SelectControl.SetActive(value: false);
		EditControl.SetActive(value: false);
		Title.text = string.Empty;
		switch (type)
		{
		case CommentEditType.EDIT:
			Title.text = "コメント編集";
			EditControl.SetActive(value: true);
			break;
		case CommentEditType.SELECT:
			Title.text = "テキスト選択";
			SelectControl.SetActive(value: true);
			break;
		}
	}

	public void OnActivate(TopicComment comment, CommentEditType type)
	{
		if (!IsActive() && !IsAnimating)
		{
			if (BodyOriginTrans == Vector3.zero)
			{
				BodyOriginTrans = InputForm.sizeDelta;
			}
			IsPosting = false;
			SetupControl(type);
			Background.alpha = 0f;
			IsAnimating = true;
			CommentData = comment.Clone();
			Content.text = comment.Content;
			MyText.text = comment.Content;
			RestFields();
			MyChildTextFitter.Fitting();
			MyRebuilder.MarkRebuild();
			ContentTrans.anchoredPosition = new Vector2(ContentTrans.anchoredPosition.x, 0f);
			base.gameObject.SetActive(value: true);
			BaseScrollbar.value = 1f;
			Background.FadeTo(1f, FadeAnimTime, 0f, iTween.EaseType.easeInSine, delegate
			{
				IsAnimating = false;
			});
		}
	}

	public void OnDeactivate()
	{
		if (IsActive() && !IsAnimating)
		{
			Background.alpha = 1f;
			IsAnimating = true;
			Background.FadeTo(0f, FadeAnimTime, 0f, iTween.EaseType.easeOutSine, delegate
			{
				IsAnimating = false;
				Background.gameObject.SetActive(value: false);
				CommentData = null;
			});
		}
	}

	public bool IsActive()
	{
		return Background.gameObject.activeInHierarchy;
	}

	public void ActivateEditForm()
	{
		Content.ActivateInputField();
		UnityEvent unityEvent = new UnityEvent();
		unityEvent.Invoke();
	}
}
