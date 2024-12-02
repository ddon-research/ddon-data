using System;
using System.Collections;
using Packet;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.Networking;
using UnityEngine.UI;
using WebRequest;

[RequireComponent(typeof(AutoLayoutRebuilder))]
public class CommentListViewer : MonoBehaviour
{
	[SerializeField]
	private GameObject Content;

	[SerializeField]
	private GameObject CommentItemPrefab;

	[SerializeField]
	private uint OffsetPageNo;

	[SerializeField]
	private ulong TopicId;

	[SerializeField]
	private ulong CalendarId;

	[SerializeField]
	private CalendarTopic.CALENDAR_TYPE Type;

	[SerializeField]
	private uint PageSize = 10u;

	[SerializeField]
	private uint TotalCommentNum;

	[SerializeField]
	private uint PageMax;

	[SerializeField]
	private Dropdown PageNavigationDownDropdown;

	[SerializeField]
	private Dropdown PageNavigationUpDropdown;

	[SerializeField]
	private GameObject CommentArea;

	[SerializeField]
	private bool IsLoaded;

	[SerializeField]
	private GameObject CommentNotice;

	[SerializeField]
	private Scrollbar CommentScrollbar;

	private IEnumerator routine;

	[SerializeField]
	private bool IsPageJumping;

	[SerializeField]
	private CanvasGroup MyCanvasGroup;

	[SerializeField]
	private float FadeTime;

	[SerializeField]
	private GameObject NavigationDownGroup;

	[SerializeField]
	private AutoLayoutRebuilder _AutoRebuilder;

	[SerializeField]
	private EditComment MyEditComment;

	[SerializeField]
	private uint _CommentMaxLimit;

	[SerializeField]
	private uint _CommentCounter;

	[SerializeField]
	protected ReloadChecker MyReloadChecker;

	protected DateTime LastUpdate;

	public AutoLayoutRebuilder AutoRebuilder
	{
		get
		{
			if (_AutoRebuilder == null)
			{
				_AutoRebuilder = GetComponent<AutoLayoutRebuilder>();
			}
			return _AutoRebuilder;
		}
		private set
		{
			_AutoRebuilder = value;
		}
	}

	public uint CommentMaxLimit
	{
		get
		{
			return _CommentMaxLimit;
		}
		private set
		{
			_CommentMaxLimit = value;
		}
	}

	public uint CommentCounter
	{
		get
		{
			return _CommentCounter;
		}
		private set
		{
			_CommentCounter = value;
		}
	}

	private void Start()
	{
		PageNavigationDownDropdown.onValueChanged.AddListener(UpdatePageJumpComments);
		PageNavigationUpDropdown.onValueChanged.AddListener(UpdatePageJumpComments);
	}

	public void OnNavigationPopBegin()
	{
		Transform transform = PageNavigationDownDropdown.transform.FindChild("Dropdown List");
		Transform transform2 = PageNavigationUpDropdown.transform.FindChild("Dropdown List");
		if (transform != null)
		{
			UnityEngine.Object.Destroy(transform.gameObject);
		}
		if (transform2 != null)
		{
			UnityEngine.Object.Destroy(transform2.gameObject);
		}
	}

	public void ClearList()
	{
		foreach (Transform componentInChild in Content.transform.GetComponentInChildren<Transform>())
		{
			UnityEngine.Object.Destroy(componentInChild.gameObject);
		}
		IsLoaded = false;
		AutoRebuilder.MarkRebuild();
	}

	private void UpdatePageSize()
	{
		uint num = TotalCommentNum / PageSize;
		if (TotalCommentNum % PageSize != 0)
		{
			num++;
		}
		PageMax = num - 1;
		PageNavigationDownDropdown.ClearOptions();
		PageNavigationUpDropdown.ClearOptions();
		for (int i = 0; i < num; i++)
		{
			PageNavigationDownDropdown.options.Add(new Dropdown.OptionData($"{i + 1:00} / {num:00}"));
			PageNavigationUpDropdown.options.Add(new Dropdown.OptionData($"{i + 1:00} / {num:00}"));
		}
		SetDropDownValue((int)OffsetPageNo);
	}

	public void InitContent(CalendarTopic topicData, uint offset)
	{
		MyCanvasGroup.alpha = 0f;
		OffsetPageNo = offset;
		TopicId = topicData.TopicId;
		DateTime lastUpdate = DateTime.Parse(topicData.ModifiedAt);
		LastUpdate = lastUpdate;
		CalendarId = topicData.CalendarId;
		Type = topicData.Type;
		CommentSet(isExistComment: false, OffsetPageNo);
		IsLoaded = false;
		AutoRebuilder.MarkRebuild();
		TotalCommentNum = topicData.CommentNum;
		MyReloadChecker.Init(delegate
		{
			CharacterCalendar.ClearCache();
			Reload();
		});
	}

	public void LoadContent()
	{
		if (!IsLoaded)
		{
			LoadContent(OffsetPageNo);
		}
	}

	public void Reload(bool NeedTopicListReload = false)
	{
		UpdatePageJumpComments(0, IsForce: true, IsReload: true);
		if (NeedTopicListReload)
		{
			SingletonMonoBehaviour<CalendarManager>.Instance.TypedTopicListView.MarkReload();
			SingletonMonoBehaviour<CalendarManager>.Instance.DayListView.MyController.MarkReload();
		}
	}

	private void OnEnable()
	{
		if (routine != null)
		{
			StartCoroutine(routine);
		}
		StartCoroutine(UpdateCheck());
	}

	private void LoadContent(uint offsetPage, bool IsReload = false)
	{
		if (IsLoaded)
		{
			MyCanvasGroup.FadeTo(0f, FadeTime, 0f, iTween.EaseType.easeInSine, delegate
			{
				LoadContentCore(offsetPage, IsReload: true);
			});
		}
		else
		{
			LoadContentCore(offsetPage);
		}
	}

	private void LoadContentCore(uint offsetPage, bool IsReload = false)
	{
		uint offset = offsetPage * PageSize;
		routine = CharacterCalendar.GetComment(delegate(TopicCommentParam result)
		{
			routine = null;
			LoadComment(result, offsetPage, IsReload);
		}, delegate(UnityWebRequest result)
		{
			AppUtility.ShowErr(result.downloadHandler.text, "TopicComment");
		}, TopicId, offset, CacheOption.TenMinute, LoadingAnimation.Default);
		if (base.gameObject.activeInHierarchy)
		{
			StartCoroutine(routine);
		}
	}

	private void LoadComment(TopicCommentParam result, uint offsetPage, bool isReload = false)
	{
		RectTransform component = CommentArea.GetComponent<RectTransform>();
		component.anchoredPosition = new Vector2(component.anchoredPosition.x, 0f);
		OffsetPageNo = offsetPage;
		TotalCommentNum = result.TotalNum;
		PageSize = result.PageSize;
		CommentMaxLimit = result.MaxLimit;
		CommentCounter = result.ActualTotalNum;
		UpdatePageSize();
		if (result.CommentList.Count == 0)
		{
			CommentSet(isExistComment: false, offsetPage);
			if (offsetPage != 0)
			{
				UpdatePrevComments();
			}
			return;
		}
		CommentSet(isExistComment: true, OffsetPageNo);
		int num = 0;
		int childCount = Content.transform.childCount;
		CommentItem commentItem = null;
		foreach (Transform componentInChild in Content.GetComponentInChildren<Transform>())
		{
			if (num >= result.CommentList.Count)
			{
				componentInChild.gameObject.SetActive(value: false);
				continue;
			}
			CommentItem component2 = componentInChild.GetComponent<CommentItem>();
			component2.UpdateContent(result.CommentList[num], this);
			componentInChild.gameObject.SetActive(value: true);
			num++;
			commentItem = component2;
		}
		int num2 = result.CommentList.Count - num;
		if (num2 > 0)
		{
			for (int i = 0; i < num2; i++)
			{
				GameObject gameObject = UnityEngine.Object.Instantiate(CommentItemPrefab);
				gameObject.transform.SetParent(Content.transform);
				gameObject.SetActive(value: true);
				gameObject.transform.localScale = new Vector3(1f, 1f, 1f);
				CommentItem component3 = gameObject.GetComponent<CommentItem>();
				component3.UpdateContent(result.CommentList[num + i], this);
				commentItem = component3;
			}
		}
		if (commentItem != null)
		{
			commentItem.SetLast();
		}
		IsLoaded = true;
		AutoRebuilder.MarkRebuild();
		if (offsetPage == 0)
		{
			DateTime lastUpdate = DateTime.Parse(result.TopicUpdatedAt);
			LastUpdate = lastUpdate;
			MyReloadChecker.MarkHideReload();
		}
		SingletonMonoBehaviour<CalendarManager>.Instance.ClanTopicDetail.ReadTopic(result.TopicUpdatedAt);
		MyCanvasGroup.FadeTo(1f, FadeTime, 0f, iTween.EaseType.easeInSine, delegate
		{
			IsPageJumping = false;
			if (isReload)
			{
				SingletonMonoBehaviour<ClanInfoCacheController>.Instance.MarkReload();
			}
		});
	}

	private void LayoutRebuild(VerticalLayoutGroup layout)
	{
		layout.CalculateLayoutInputHorizontal();
		layout.CalculateLayoutInputVertical();
		layout.SetLayoutHorizontal();
		layout.SetLayoutVertical();
	}

	private void CommentSet(bool isExistComment, uint offsetPage)
	{
		if (isExistComment)
		{
			CommentNotice.SetActive(value: false);
			CommentArea.SetActive(value: true);
			Content.SetActive(value: true);
			NavigationDownGroup.SetActive(value: true);
			return;
		}
		CommentNotice.SetActive(value: true);
		if (offsetPage == 0)
		{
			CommentArea.SetActive(value: false);
			return;
		}
		Content.SetActive(value: false);
		NavigationDownGroup.SetActive(value: false);
	}

	public void UpdatePrevComments()
	{
		EventSystem.current.SetSelectedGameObject(null);
		uint num = 0u;
		if (OffsetPageNo != 0)
		{
			num = OffsetPageNo - 1;
		}
		if (num != OffsetPageNo)
		{
			LoadContent(num);
			SetDropDownValue((int)num);
		}
	}

	public void UpdateNextComments()
	{
		EventSystem.current.SetSelectedGameObject(null);
		uint num = OffsetPageNo;
		if (OffsetPageNo < PageMax)
		{
			num = OffsetPageNo + 1;
		}
		if (num != OffsetPageNo)
		{
			LoadContent(num);
			SetDropDownValue((int)num);
		}
	}

	public void UpdatePageJumpComments(int index)
	{
		UpdatePageJumpComments(index, IsForce: false, IsReload: false);
	}

	public void UpdatePageJumpComments(int index, bool IsForce = false, bool IsReload = false)
	{
		if (!IsPageJumping)
		{
			IsPageJumping = true;
			uint num = (uint)index;
			if (num > PageMax)
			{
				num = PageMax;
			}
			if (num < 0)
			{
				num = 0u;
			}
			if (num == OffsetPageNo && !IsForce)
			{
				IsPageJumping = false;
				return;
			}
			LoadContent(num, IsReload);
			SetDropDownValue((int)num);
			EventSystem.current.SetSelectedGameObject(null);
		}
	}

	private void SetDropDownValue(int value)
	{
		PageNavigationDownDropdown.value = value;
		PageNavigationDownDropdown.RefreshShownValue();
		PageNavigationUpDropdown.value = value;
		PageNavigationUpDropdown.RefreshShownValue();
	}

	public void EditComment(TopicComment comment, EditComment.CommentEditType type)
	{
		MyEditComment.OnActivate(comment, type);
	}

	private IEnumerator UpdateCheck()
	{
		while (base.gameObject.activeInHierarchy)
		{
			StartCoroutine(CharacterCalendar.PostListUpdatedInfo(value: new CalendarUpdateInfo
			{
				Type = Type,
				UpdateDate = CalendarTopic.DateTimeToString(LastUpdate)
			}, onResult: delegate(CalendarUpdateInfoListParam result)
			{
				bool flag = false;
				foreach (CalendarUpdateInfo info in result.infoList)
				{
					if (info.CalendarId == CalendarId && info.TopicId == TopicId && info.Type == Type)
					{
						flag = true;
						break;
					}
				}
				if (result.infoList.Count > 0 && flag)
				{
					MyReloadChecker.MarkShowReload();
				}
				else
				{
					MyReloadChecker.MarkHideReload();
				}
			}, onError: delegate
			{
			}));
			yield return new WaitForSeconds(CalendarConstParams.RELOAD_INTERVAL);
		}
	}

	public void DestroyCommentImage()
	{
		foreach (Transform componentInChild in Content.GetComponentInChildren<Transform>())
		{
			CommentItem component = componentInChild.GetComponent<CommentItem>();
			component.DestroyImage();
		}
	}
}
