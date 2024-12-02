using System;
using System.Collections;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using WebRequest;

[RequireComponent(typeof(AutoLayoutRebuilder))]
public class TopicDetail : ViewController
{
	[SerializeField]
	protected Text BeginDate;

	[SerializeField]
	protected Text EndDate;

	[SerializeField]
	protected Text TopicTitle;

	[SerializeField]
	protected RegexHypertext Content;

	[SerializeField]
	private Text LikeUpdatedAt;

	[SerializeField]
	protected CalendarTopic.CALENDAR_TYPE Type;

	[SerializeField]
	protected ulong m_TopicId;

	[SerializeField]
	protected ulong m_CalendarId;

	protected float FadeTime = CalendarConstParams.RELOAD_ANIM_TIME;

	[SerializeField]
	protected LikeButton m_LikeButton;

	public const string REGEX_URL = "https?://[0-9a-zA-Z/:%#\\$&\\?\\(\\)~\\.=\\+\\-_]+";

	protected CalendarTopic TopicData;

	[SerializeField]
	protected CustomMenu customMenu;

	private bool IsDeleting;

	[SerializeField]
	protected ReloadChecker MyReloadChecker;

	[SerializeField]
	protected CanvasGroup MyCanvasGroup;

	protected DateTime LastUpdate;

	[SerializeField]
	private BannerElement BannerPrefab;

	[SerializeField]
	protected ImageGrid MyImageGrid;

	private List<BannerElement> BannerList = new List<BannerElement>();

	private IEnumerator routine;

	[SerializeField]
	private AutoLayoutRebuilder _MyRebuilder;

	[SerializeField]
	protected Scrollbar BaseScrollbar;

	private bool NeedReload;

	[SerializeField]
	protected bool LikeIsPosting;

	protected object LikethisLock = new object();

	[SerializeField]
	protected bool ReportIsPosting;

	protected object ReportthisLock = new object();

	[SerializeField]
	private bool _IsFromTypedList;

	[SerializeField]
	private GameObject NavigationControl;

	private bool TopicNavigating;

	protected AutoLayoutRebuilder MyRebuilder
	{
		get
		{
			if (_MyRebuilder == null)
			{
				_MyRebuilder = GetComponent<AutoLayoutRebuilder>();
			}
			return _MyRebuilder;
		}
		private set
		{
			_MyRebuilder = value;
		}
	}

	private bool IsFromTypedList
	{
		get
		{
			return _IsFromTypedList;
		}
		set
		{
			_IsFromTypedList = value;
			if (NavigationControl != null)
			{
				NavigationControl.SetActive(value);
			}
		}
	}

	public void Start()
	{
		Content.SetClickableByRegex("https?://[0-9a-zA-Z/:%#\\$&\\?\\(\\)~\\.=\\+\\-_]+", Color.cyan, delegate(string url)
		{
			Debug.Log(url);
			Application.OpenURL(url);
		});
	}

	protected void InitControl(CalendarTopic topic)
	{
		customMenu.gameObject.SetActive(value: true);
		switch (topic.Type)
		{
		case CalendarTopic.CALENDAR_TYPE.PRIVATE:
			InitControlPrivate(topic);
			break;
		case CalendarTopic.CALENDAR_TYPE.CLAN:
			InitControlClan(topic, IsBoard: false);
			break;
		case CalendarTopic.CALENDAR_TYPE.CLAN_MESSAGE_BOARD:
			SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.MarkReload();
			InitControlClan(topic, IsBoard: true);
			break;
		case CalendarTopic.CALENDAR_TYPE.EVENT:
			InitControlOfficial(topic);
			break;
		}
	}

	private void InitControlPrivate(CalendarTopic topic)
	{
		List<CustomMenuContentData> list = new List<CustomMenuContentData>();
		list.Add(new CustomMenuContentData
		{
			Name = "トピックを編集",
			OnClick = delegate
			{
				OpenEditTopic();
			}
		});
		list.Add(new CustomMenuContentData
		{
			Name = "トピックを削除",
			OnClick = delegate
			{
				DeleteTopic();
			}
		});
		List<CustomMenuContentData> content = list;
		customMenu.SetContent(content);
	}

	private void InitControlClan(CalendarTopic topic, bool IsBoard)
	{
		SingletonMonoBehaviour<ClanInfoCacheController>.Instance.UpdateClanMemberInfo(delegate
		{
			string text = ((!IsBoard) ? "トピック" : "テーマ");
			List<CustomMenuContentData> list = new List<CustomMenuContentData>();
			uint characterID = SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData.CharacterID;
			ClanMemberListElement characterInfo = SingletonMonoBehaviour<ClanInfoCacheController>.Instance.GetCharacterInfo(characterID);
			if (characterInfo != null && (characterInfo.MemberRank == 1 || characterInfo.MemberRank == 2))
			{
				list.Add(new CustomMenuContentData
				{
					Name = text + "を編集",
					OnClick = delegate
					{
						OpenEditTopic();
					}
				});
				if (!IsBoard)
				{
					list.Add(new CustomMenuContentData
					{
						Name = text + "を削除",
						OnClick = delegate
						{
							DeleteTopic();
						}
					});
				}
			}
			if (characterID != topic.CharacterId)
			{
				if (list.Count > 0)
				{
					list.Add(new CustomMenuContentData
					{
						IsBorder = true
					});
				}
				if (topic.IsReported)
				{
					list.Add(new CustomMenuContentData
					{
						TextColor = Color.gray,
						Name = "この" + text + "は通報済み",
						OnClick = delegate
						{
							SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "この" + text + "はすでに通報済みです。");
						}
					});
				}
				else
				{
					list.Add(new CustomMenuContentData
					{
						Name = "この" + text + "を通報する",
						OnClick = delegate
						{
							ReportTopic();
						}
					});
				}
			}
			if (list.Count == 0)
			{
				customMenu.gameObject.SetActive(value: false);
			}
			customMenu.SetContent(list);
		});
	}

	private void InitControlOfficial(CalendarTopic topic)
	{
		SingletonMonoBehaviour<ClanInfoCacheController>.Instance.UpdateClanMemberInfo(delegate
		{
			List<CustomMenuContentData> list = new List<CustomMenuContentData>
			{
				new CustomMenuContentData
				{
					Name = "引用してプライベートトピック作成",
					OnClick = delegate
					{
						CreateTopic(CalendarTopic.CALENDAR_TYPE.PRIVATE);
					}
				}
			};
			if (!topic.IsMaintainer)
			{
				uint characterID = SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData.CharacterID;
				ClanMemberListElement characterInfo = SingletonMonoBehaviour<ClanInfoCacheController>.Instance.GetCharacterInfo(characterID);
				if (characterInfo != null && (characterInfo.MemberRank == 1 || characterInfo.MemberRank == 2))
				{
					list.Add(new CustomMenuContentData
					{
						Name = "引用してクラントピック作成",
						OnClick = delegate
						{
							CreateTopic(CalendarTopic.CALENDAR_TYPE.CLAN);
						}
					});
				}
				list.Add(new CustomMenuContentData
				{
					IsBorder = true
				});
				list.Add(new CustomMenuContentData
				{
					Name = "イベントタイトルをツイート",
					OnClick = delegate
					{
						TitleTweet();
					}
				});
			}
			customMenu.SetContent(list);
		});
	}

	public void OnEnable()
	{
		if (routine != null)
		{
			StartCoroutine(routine);
			routine = null;
		}
		LikeIsPosting = false;
		ReportIsPosting = false;
	}

	public void OpenEditTopic()
	{
		SingletonMonoBehaviour<CalendarManager>.Instance.EditTopic.UpdateContent(TopicData, this);
		SingletonMonoBehaviour<NavigationViewController>.Instance.Push(SingletonMonoBehaviour<CalendarManager>.Instance.EditTopic);
	}

	private void DeleteTopic()
	{
		SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK_Cancel, "トピック削除確認", "本当にトピックを削除しても\nよろしいですか？", delegate(ModalDialog.Result res)
		{
			if (!IsDeleting && res == ModalDialog.Result.OK)
			{
				IsDeleting = true;
				StartCoroutine(CharacterCalendar.DeleteTopic(delegate
				{
					SingletonMonoBehaviour<AppUtility>.Instance.ShowDialogAndPop("完了", "トピックを削除しました。", delegate
					{
						CharacterCalendar.ClearCache();
						SingletonMonoBehaviour<CalendarManager>.Instance.CalendarController.MarkReload();
						SingletonMonoBehaviour<CalendarManager>.Instance.TypedTopicListView.MarkReload();
						SingletonMonoBehaviour<CalendarManager>.Instance.DayListView.MyController.MarkReload();
						SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.MarkReload();
					});
					IsDeleting = false;
				}, delegate(UnityWebRequest result)
				{
					AppUtility.ShowErr(result.downloadHandler.text, "CalendarTopic");
					IsDeleting = false;
				}, TopicData.CalendarId, (int)TopicData.Type, LoadingAnimation.Default));
			}
		});
	}

	public override void OnNavigationPushEnd()
	{
		if (Type != CalendarTopic.CALENDAR_TYPE.CLAN_MESSAGE_BOARD)
		{
			ReloadContent();
		}
		CalendarTopic.CALENDAR_TYPE type = Type;
		if (type == CalendarTopic.CALENDAR_TYPE.EVENT)
		{
			StartCoroutine(UpdateCheck());
		}
	}

	public void Update()
	{
		if (NeedReload)
		{
			ReloadContent();
			NeedReload = false;
		}
	}

	public override void OnNavigationPopBegin()
	{
		routine = null;
		MyImageGrid.DestroyImages();
	}

	public void MarkReload()
	{
		NeedReload = true;
	}

	public void UpdateContent(CalendarTopic topic, bool isTypedList)
	{
		UpdateContent(topic);
		IsFromTypedList = isTypedList;
	}

	public virtual void UpdateContent(CalendarTopic topic)
	{
		NeedReload = false;
		Type = topic.Type;
		InitControl(topic);
		BaseScrollbar.value = 1f;
		MyCanvasGroup.alpha = 1f;
		m_TopicId = topic.TopicId;
		m_CalendarId = topic.CalendarId;
		TopicData = topic;
		IsFromTypedList = false;
		if (!topic.IsMaintainer)
		{
			ReadTopic();
		}
		Content.RemoveClickable();
		DateTime dateTime = DateTime.Parse(topic.BeginDate);
		DateTime dateTime2 = DateTime.Parse(topic.EndDate);
		DateTime lastUpdate = DateTime.Parse(topic.ModifiedAt);
		LastUpdate = lastUpdate;
		BeginDate.text = dateTime.ToString("yyyy.MM.dd HH:mm");
		EndDate.text = dateTime2.ToString("yyyy.MM.dd HH:mm");
		if ("1900-01-01T00:00:00+09:00" == topic.BeginDate)
		{
			BeginDate.text = "指定なし";
		}
		if ("2100-01-01T00:00:00+09:00" == topic.EndDate)
		{
			EndDate.text = "指定なし";
		}
		TopicTitle.text = topic.Title;
		Content.text = topic.Content;
		Content.SetClickableByRegex("https?://[0-9a-zA-Z/:%#\\$&\\?\\(\\)~\\.=\\+\\-_]+", Color.cyan, delegate(string url)
		{
			Debug.Log(url);
			Application.OpenURL(url);
		});
		if (Type == CalendarTopic.CALENDAR_TYPE.EVENT)
		{
			DateTime dateTime3 = DateTime.Parse(topic.LikeUpdatedAt);
			LikeUpdatedAt.text = dateTime3.ToString("yyyy.MM.dd HH:mm:ss");
			m_LikeButton.UpdateContent(topic.IsLiked, topic.LikeNum);
		}
		if (topic.Content.Length > 0)
		{
			MyImageGrid.UpdateContent(topic.ImageInfoList);
		}
		else
		{
			MyCanvasGroup.alpha = 0f;
		}
		MyRebuilder.MarkRebuild();
		MyReloadChecker.Init(delegate
		{
			CharacterCalendar.ClearCache();
			ReloadContent();
		});
	}

	public void ReloadContent(Action onCallBack = null)
	{
		SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: true);
		StartCoroutine(CharacterCalendar.GetSelectTopic(delegate(CalendarTopic result)
		{
			MyCanvasGroup.FadeTo(0f, FadeTime, 0f, iTween.EaseType.easeOutSine, delegate
			{
				UpdateContent(result, IsFromTypedList);
				MyCanvasGroup.alpha = 0f;
				MyCanvasGroup.FadeTo(1f, FadeTime, 0f, iTween.EaseType.easeInSine, delegate
				{
					SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
					if (onCallBack != null)
					{
						onCallBack();
					}
				});
			});
		}, delegate(UnityWebRequest result)
		{
			SingletonMonoBehaviour<LoadController>.Instance.SetLoadActive(active: false);
			AppUtility.ShowErr(result.downloadHandler.text, "CalendarTopic", IsPop: false);
		}, (int)TopicData.Type, TopicData.TopicId, CacheOption.TenMinute));
	}

	public void LikeUpdate()
	{
		if (TopicData == null)
		{
			Debug.Log("TopicDataがnullです");
			return;
		}
		lock (LikethisLock)
		{
			if (LikeIsPosting)
			{
				return;
			}
			LikeIsPosting = true;
		}
		CalendarTopic postData = TopicData;
		postData.IsLiked = !postData.IsLiked;
		StartCoroutine(CharacterCalendar.PostTopic(delegate
		{
			TopicData.IsLiked = postData.IsLiked;
			if (TopicData.Type != CalendarTopic.CALENDAR_TYPE.EVENT)
			{
				if (TopicData.IsLiked)
				{
					TopicData.LikeNum++;
				}
				else
				{
					TopicData.LikeNum--;
				}
			}
			m_LikeButton.UpdateContent(TopicData.IsLiked, TopicData.LikeNum, Type);
			CharacterCalendar.ClearCache_GetTopicStringInt32Int32Int32Int32Int32();
			CharacterCalendar.ClearCache_GetSelectTopicInt32UInt64();
			SingletonMonoBehaviour<CalendarManager>.Instance.TypedTopicListView.MarkReload();
			LikeIsPosting = false;
		}, delegate(UnityWebRequest result)
		{
			AppUtility.ShowErr(result.downloadHandler.text, "CalendarTopic", IsPop: false);
			LikeIsPosting = false;
		}, "like", postData, LoadingAnimation.Default));
	}

	public void ReportTopic()
	{
		SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK_Cancel, "確認", "このトピックを本当に通報しますか？", delegate(ModalDialog.Result res)
		{
			if (res == ModalDialog.Result.OK)
			{
				lock (ReportthisLock)
				{
					if (ReportIsPosting)
					{
						return;
					}
					ReportIsPosting = true;
				}
				string text = "タイトル：" + TopicData.Title;
				text = text + "\n" + TopicData.Content;
				ReportTopicInfo value = new ReportTopicInfo(TopicData.CharacterId, TopicData.TopicId, 0uL, text);
				StartCoroutine(WebRequest.Report.PostTopic(delegate
				{
					SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "このトピックを通報しました。");
					CharacterCalendar.ClearCache_GetSelectTopicInt32UInt64();
					ReloadContent();
					ReportIsPosting = false;
				}, delegate(UnityWebRequest result)
				{
					AppUtility.ShowErr(result.downloadHandler.text, "ReportTopicInfo");
					ReportIsPosting = false;
				}, value, LoadingAnimation.Default));
			}
		});
	}

	public void BlockUser()
	{
		SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK_Cancel, "確認", "このキャラクターを本当にブロックしますか？", delegate(ModalDialog.Result res)
		{
			if (res == ModalDialog.Result.OK)
			{
				AppBlackListParam valueParam = new AppBlackListParam
				{
					BlackList = 
					{
						new Packet.AppBlackList(TopicData.CharacterId, isDeleted: false)
					}
				};
				StartCoroutine(WebRequest.AppBlackList.PostList(delegate
				{
					SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "このキャラクターをブロックしました。");
					CharacterCalendar.ClearCache_GetCommentUInt64UInt32();
				}, delegate(UnityWebRequest result)
				{
					AppUtility.ShowErr(result.downloadHandler.text, "AppBlackList");
				}, valueParam, LoadingAnimation.Default));
			}
		});
	}

	protected void TitleTweet()
	{
		string text = "%0a";
		string text2 = WWW.EscapeURL("ドラゴンズドグマオンラインで気になるイベントはコレ→") + text + WWW.EscapeURL(TopicData.Title);
		string text3 = "https://twitter.com/intent/tweet?hashtags=DDON&text=" + text2;
		if (TopicData.ImageInfoList.Count > 0 && TopicData.ImageInfoList[0].LinkUrl.Length > 0)
		{
			text3 = text3 + "&url=" + TopicData.ImageInfoList[0].LinkUrl;
		}
		Application.OpenURL(text3);
	}

	public void CreateTopic(CalendarTopic.CALENDAR_TYPE type)
	{
		SingletonMonoBehaviour<CalendarManager>.Instance.CreateTopic.UpdateContent(type, TopicData);
		SingletonMonoBehaviour<NavigationViewController>.Instance.Push(SingletonMonoBehaviour<CalendarManager>.Instance.CreateTopic);
	}

	public void OpenProfile()
	{
		SingletonMonoBehaviour<ProfileManager>.Instance.OpenProfilePlayer(TopicData.CharacterId);
	}

	protected IEnumerator UpdateCheck()
	{
		while (base.gameObject.activeInHierarchy)
		{
			CalendarUpdateInfo info = new CalendarUpdateInfo
			{
				Type = Type,
				UpdateDate = CalendarTopic.DateTimeToString(LastUpdate)
			};
			if (TopicData == null)
			{
				yield return new WaitForSeconds(CalendarConstParams.RELOAD_INTERVAL);
			}
			StartCoroutine(CharacterCalendar.PostListUpdatedInfo(delegate(CalendarUpdateInfoListParam result)
			{
				bool flag = false;
				if (TopicData != null)
				{
					foreach (CalendarUpdateInfo info2 in result.infoList)
					{
						if (info2.CalendarId == TopicData.CalendarId && info2.TopicId == TopicData.TopicId && info2.Type == TopicData.Type)
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
				}
			}, delegate
			{
			}, info));
			yield return new WaitForSeconds(CalendarConstParams.RELOAD_INTERVAL);
		}
	}

	public void ReadTopic()
	{
		ReadTopic(TopicData.ModifiedAt);
	}

	public void ReadTopic(string update)
	{
		CalendarUpdateInfo calendarUpdateInfo = new CalendarUpdateInfo();
		calendarUpdateInfo.CalendarId = TopicData.CalendarId;
		calendarUpdateInfo.TopicId = TopicData.TopicId;
		calendarUpdateInfo.Type = TopicData.Type;
		calendarUpdateInfo.UpdateDate = update;
		CalendarUpdateInfo info = calendarUpdateInfo;
		SingletonMonoBehaviour<CalendarUpdateInfoManager>.Instance.ReadTopic(info);
	}

	public void ShowNavigationTopic(bool IsNext)
	{
		if (!TopicNavigating)
		{
			TopicNavigating = true;
			CalendarTopic selectTopic = SingletonMonoBehaviour<CalendarManager>.Instance.TypedTopicListView.GetSelectTopic(TopicData, IsNext);
			if (selectTopic != null)
			{
				TopicData = selectTopic;
				ReloadContent();
				TopicNavigating = false;
			}
		}
	}
}
