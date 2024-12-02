using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using DDOAppMaster.Enum.TopInformation;
using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class HomeNpcManager : SingletonMonoBehaviour<HomeNpcManager>
{
	private enum Routine
	{
		Awake,
		Init,
		GetThink,
		GetCageotryInfo,
		GetTalk,
		OpenWindow,
		NpcTalk,
		CloseWait,
		CloseWindow,
		Wait
	}

	private class PageInfo
	{
		public string Text;

		public uint EmoteNa;

		public PageInfo(string text, uint emoteNo)
		{
			Text = text;
			EmoteNa = emoteNo;
		}
	}

	private class NpcTalkInfo
	{
		private HomeNpcManager Manager;

		private int PageIndex;

		private List<PageInfo> Pages = new List<PageInfo>();

		public NpcTalkInfo(HomeNpcManager manager)
		{
			Manager = manager;
		}

		public bool SetText(string SourceText, AppInfoMessageType type, List<TopInfomationKeyValuePair> inParams, List<CalendarTopic> topicList)
		{
			PageIndex = 0;
			Pages.Clear();
			uint emoteNo = 1u;
			Regex regex = new Regex("<inparam,(?<no>\\s\\d+)>");
			MatchCollection matchCollection = regex.Matches(SourceText);
			foreach (Match item in matchCollection)
			{
				if (item.Groups.Count != 2)
				{
					continue;
				}
				int result = 0;
				if (int.TryParse(item.Groups[1].Value.Trim(), out result))
				{
					foreach (TopInfomationKeyValuePair inParam in inParams)
					{
						if (inParam.Key == (AppInfoConditionType)result)
						{
							SourceText = SourceText.Replace(item.Groups[0].Value, inParam.Value.ToString());
							break;
						}
					}
					continue;
				}
				Debug.LogError("リサ会話tagエラー" + SourceText);
				return false;
			}
			Regex regex2 = new Regex("<emote,(?<no>\\s\\d+)>");
			MatchCollection matchCollection2 = regex2.Matches(SourceText);
			foreach (Match item2 in matchCollection2)
			{
				if (item2.Groups.Count == 2)
				{
					int result2 = 0;
					if (!int.TryParse(item2.Groups[1].Value.Trim(), out result2))
					{
						Debug.LogError("リサ会話エモートタグエラー" + SourceText);
						return false;
					}
					SourceText = SourceText.Replace(item2.Groups[0].Value, string.Empty);
					emoteNo = (uint)result2;
				}
			}
			switch (type)
			{
			case AppInfoMessageType.Topic_Offical:
				if (topicList == null)
				{
					return false;
				}
				if (!SourceText.Contains("<officialtopic>"))
				{
					break;
				}
				foreach (CalendarTopic topic in topicList)
				{
					if (topic.Type == CalendarTopic.CALENDAR_TYPE.EVENT)
					{
						SourceText = SourceText.Replace("<officialtopic>", topic.Title);
					}
				}
				break;
			case AppInfoMessageType.Topic_Clan:
				if (topicList == null)
				{
					return false;
				}
				if (!SourceText.Contains("<clantopic>"))
				{
					break;
				}
				foreach (CalendarTopic topic2 in topicList)
				{
					if (topic2.Type == CalendarTopic.CALENDAR_TYPE.CLAN)
					{
						SourceText = SourceText.Replace("<clantopic>", topic2.Title);
					}
				}
				break;
			case AppInfoMessageType.Topic_Private:
				if (topicList == null)
				{
					return false;
				}
				if (SourceText.Contains("<privatetopic>"))
				{
					foreach (CalendarTopic topic3 in topicList)
					{
						if (topic3.Type == CalendarTopic.CALENDAR_TYPE.PRIVATE)
						{
							SourceText = SourceText.Replace("<privatetopic>", topic3.Title);
						}
					}
					break;
				}
				Debug.LogError("リサ会話トピックタグエラー" + SourceText);
				return false;
			}
			string[] separator = new string[1] { "<nextpage>" };
			string[] array = SourceText.Split(separator, StringSplitOptions.None);
			string[] array2 = array;
			foreach (string text in array2)
			{
				Pages.Add(new PageInfo(text.Trim(), emoteNo));
			}
			return true;
		}

		public PageInfo MoveNextPage()
		{
			if (PageIndex >= Pages.Count)
			{
				return null;
			}
			PageInfo result = Pages[PageIndex];
			PageIndex++;
			return result;
		}

		public bool IsEnd()
		{
			return PageIndex >= Pages.Count;
		}

		public int GetPageNum()
		{
			return Pages.Count;
		}
	}

	private CanvasGroup _CG;

	private RectTransform _rt;

	[SerializeField]
	private float MovingVel = -100f;

	[SerializeField]
	private HomeBGController BGController;

	[SerializeField]
	private Image NpcImage;

	private CanvasGroup NpcCanvasGroup;

	[SerializeField]
	private Sprite[] EmoteSprites;

	[SerializeField]
	private TextAlphaSending TextSending;

	[SerializeField]
	private Image NextPageIcon;

	[SerializeField]
	private RectTransform DialogWindow;

	[SerializeField]
	private float NextPageWaitSecond = 5f;

	[SerializeField]
	private float CloseWaitSecond = 3f;

	[SerializeField]
	private float NextTalkWaitSecond = 5f;

	[SerializeField]
	private uint GreetingEmoteNo = 1u;

	[SerializeField]
	private uint FootworkEmoteNo = 4u;

	[SerializeField]
	private uint ThinkingEmoteNo = 6u;

	[SerializeField]
	private float ThinkingWaitSecond = 3f;

	[SerializeField]
	private float ThinkingWaitRandomSecond = 3f;

	[SerializeField]
	private CanvasGroup ThinkBaloon;

	[SerializeField]
	private CanvasGroup LightBaloon;

	private GameDateTime NowGameTime;

	private uint NowWeatherId;

	private uint NowMoonId;

	private uint NowNpcEmoteNo;

	private Routine CurrentRoutine;

	private uint SubRoutineNo;

	private NpcTalkInfo TalkInfo;

	private float RoutineDeltaTime;

	private float RoutineDeltaTime2;

	private AppInfoMessageType CurrentMessageType;

	private int CurrentScheduleIndex;

	private AppInfoMessageType[] MessageTypeSchedules = new AppInfoMessageType[10]
	{
		AppInfoMessageType.Craft,
		AppInfoMessageType.Bazaar,
		AppInfoMessageType.Topic_Offical,
		AppInfoMessageType.Mail_User,
		AppInfoMessageType.Mail_Ope,
		AppInfoMessageType.Catting,
		AppInfoMessageType.Gift,
		AppInfoMessageType.Catting,
		AppInfoMessageType.Topic_Clan,
		AppInfoMessageType.Topic_Private
	};

	private List<TopInfomationKeyValuePair> RequestParams = new List<TopInfomationKeyValuePair>();

	private List<CalendarTopic> TopicListResult;

	public CanvasGroup CG => _CG ?? (_CG = GetComponent<CanvasGroup>());

	public RectTransform RT => _rt ?? (_rt = GetComponent<RectTransform>());

	private void Start()
	{
		DialogWindow.gameObject.SetActive(value: false);
		NextPageIcon.gameObject.SetActive(value: false);
		NpcCanvasGroup = NpcImage.GetComponent<CanvasGroup>();
		TalkInfo = new NpcTalkInfo(this);
		MessageTypeSchedules = MessageTypeSchedules.OrderBy((AppInfoMessageType i) => Guid.NewGuid()).ToArray();
	}

	private void Update()
	{
		UpdateRoutine();
		CG.alpha = Mathf.Clamp01(BGController.NpcAlpha);
		Vector2 anchoredPosition = RT.anchoredPosition;
		anchoredPosition.x = MovingVel * BGController.NpcMoving;
		RT.anchoredPosition = anchoredPosition;
	}

	private void OnEnable()
	{
		DialogWindow.gameObject.SetActive(value: false);
		NextPageIcon.gameObject.SetActive(value: false);
		ThinkBaloon.gameObject.SetActive(value: false);
		LightBaloon.gameObject.SetActive(value: false);
		TextSending.Text.text = string.Empty;
		if (CurrentRoutine != 0)
		{
			SetRoutine(Routine.Init);
		}
	}

	public void SetEnvironment(GameDateTime time, uint weather, uint moon)
	{
		NowGameTime = time;
		NowWeatherId = weather;
		NowMoonId = moon;
	}

	public void SetNpcEmote(uint no, float waitSecond, Action onComplete)
	{
		if (no >= EmoteSprites.Count())
		{
			onComplete();
			return;
		}
		if (EmoteSprites[no] == null)
		{
			onComplete();
			return;
		}
		if (NowNpcEmoteNo == no)
		{
			onComplete();
			return;
		}
		NpcCanvasGroup.FadeTo(0f, 0.5f, waitSecond, iTween.EaseType.easeOutSine, delegate
		{
			NowNpcEmoteNo = no;
			NpcImage.sprite = EmoteSprites[no];
			NpcCanvasGroup.FadeTo(1f, 0.5f, 0f, iTween.EaseType.easeOutSine, onComplete);
		});
	}

	private void SetRoutine(Routine r)
	{
		CurrentRoutine = r;
		SubRoutineNo = 0u;
		RoutineDeltaTime = 0f;
		Debug.Log(string.Concat(CurrentRoutine, " : ", CurrentMessageType));
	}

	private void UpdateRoutine()
	{
		RoutineDeltaTime += Time.deltaTime;
		switch (CurrentRoutine)
		{
		case Routine.Awake:
			Routine_Awake();
			break;
		case Routine.Init:
			Routine_Init();
			break;
		case Routine.GetThink:
			Routine_GetThink();
			break;
		case Routine.GetCageotryInfo:
			Routine_GetCategoryInfo();
			break;
		case Routine.GetTalk:
			Routine_GetTalk();
			break;
		case Routine.OpenWindow:
			Routine_OpenWindow();
			break;
		case Routine.NpcTalk:
			Routine_NpcTalk();
			break;
		case Routine.CloseWait:
			Routine_CloseWait();
			break;
		case Routine.CloseWindow:
			Routine_CloseWindow();
			break;
		case Routine.Wait:
			Routine_Wait();
			break;
		}
	}

	private void Routine_Awake()
	{
		if (SubRoutineNo == 0)
		{
			SubRoutineNo++;
			NpcCanvasGroup.alpha = 0f;
			SetNpcEmote(GreetingEmoteNo, 2f, delegate
			{
				CurrentMessageType = AppInfoMessageType.Greeting;
				SetRoutine(Routine.GetTalk);
			});
		}
	}

	private void Routine_Init()
	{
		if (SubRoutineNo != 0)
		{
			return;
		}
		NextPageIcon.gameObject.SetActive(value: false);
		if (CurrentScheduleIndex >= MessageTypeSchedules.Length)
		{
			CurrentScheduleIndex = 0;
			MessageTypeSchedules = MessageTypeSchedules.OrderBy((AppInfoMessageType i) => Guid.NewGuid()).ToArray();
		}
		CurrentMessageType = MessageTypeSchedules[CurrentScheduleIndex];
		CurrentScheduleIndex++;
		SubRoutineNo++;
		SetNpcEmote(ThinkingEmoteNo, 0f, delegate
		{
			if (!ThinkBaloon.gameObject.activeSelf)
			{
				ThinkBaloon.gameObject.SetActive(value: true);
				ThinkBaloon.alpha = 0f;
				ThinkBaloon.FadeTo(1f, 0.3f, 0f, iTween.EaseType.easeOutCubic);
			}
			RoutineDeltaTime2 = UnityEngine.Random.value * ThinkingWaitRandomSecond;
			SetRoutine(Routine.GetThink);
		});
	}

	private void Routine_GetThink()
	{
		if (RoutineDeltaTime >= ThinkingWaitSecond + RoutineDeltaTime2)
		{
			SetRoutine(Routine.GetCageotryInfo);
		}
	}

	private void AddRequestParam(AppInfoConditionType type, int value)
	{
		RequestParams.Add(new TopInfomationKeyValuePair(type, value));
	}

	private void Routine_GetCategoryInfo()
	{
		if (SubRoutineNo != 0)
		{
			return;
		}
		RequestParams.Clear();
		SubRoutineNo = 1u;
		DateTime now = DateTime.Now;
		switch (CurrentMessageType)
		{
		case AppInfoMessageType.Catting:
			if (NowGameTime == null)
			{
				SetRoutine(Routine.Wait);
				break;
			}
			AddRequestParam(AppInfoConditionType.LestaniaHour, NowGameTime.Hh);
			AddRequestParam(AppInfoConditionType.LestaniaAgeObTheMoon, (int)NowMoonId);
			AddRequestParam(AppInfoConditionType.LestaniaWeather, (int)NowWeatherId);
			AddRequestParam(AppInfoConditionType.Gold, (int)SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData.Gold);
			SetRoutine(Routine.GetTalk);
			break;
		case AppInfoMessageType.Greeting:
			SetRoutine(Routine.GetTalk);
			break;
		case AppInfoMessageType.Topic_Offical:
			StartCoroutine(CharacterCalendar.GetTopic(delegate(CalendarTopicParam res)
			{
				if (res.TopicList == null)
				{
					SetRoutine(Routine.Wait);
				}
				else
				{
					int num = 0;
					foreach (CalendarTopic topic in res.TopicList)
					{
						if (topic.Type == CalendarTopic.CALENDAR_TYPE.EVENT)
						{
							num++;
						}
					}
					if (res.TopicList.Count >= 0)
					{
						TopicListResult = res.TopicList.OrderBy((CalendarTopic i) => Guid.NewGuid()).ToList();
					}
					AddRequestParam(AppInfoConditionType.Topic_NumEvent, num);
					SetRoutine(Routine.GetTalk);
				}
			}, null, "day_list", 4, now.Year, now.Month, now.Day, 0));
			break;
		case AppInfoMessageType.Topic_Clan:
			StartCoroutine(CharacterCalendar.GetTopic(delegate(CalendarTopicParam res)
			{
				if (res.TopicList == null)
				{
					SetRoutine(Routine.Wait);
				}
				else
				{
					int num2 = 0;
					foreach (CalendarTopic topic2 in res.TopicList)
					{
						if (topic2.Type == CalendarTopic.CALENDAR_TYPE.CLAN)
						{
							num2++;
						}
					}
					if (res.TopicList.Count >= 0)
					{
						TopicListResult = res.TopicList.OrderBy((CalendarTopic i) => Guid.NewGuid()).ToList();
					}
					AddRequestParam(AppInfoConditionType.Topic_NumClan, num2);
					SetRoutine(Routine.GetTalk);
				}
			}, delegate
			{
				SetRoutine(Routine.Init);
			}, "day_list", 2, now.Year, now.Month, now.Day, 0));
			break;
		case AppInfoMessageType.Topic_Private:
			StartCoroutine(CharacterCalendar.GetTopic(delegate(CalendarTopicParam res)
			{
				if (res.TopicList == null)
				{
					SetRoutine(Routine.Wait);
				}
				else
				{
					int num3 = 0;
					foreach (CalendarTopic topic3 in res.TopicList)
					{
						if (topic3.Type == CalendarTopic.CALENDAR_TYPE.PRIVATE)
						{
							num3++;
						}
					}
					if (res.TopicList.Count >= 0)
					{
						TopicListResult = res.TopicList.OrderBy((CalendarTopic i) => Guid.NewGuid()).ToList();
					}
					AddRequestParam(AppInfoConditionType.Topic_NumPrivate, num3);
					SetRoutine(Routine.GetTalk);
				}
			}, null, "day_list", 1, now.Year, now.Month, now.Day, 0));
			break;
		case AppInfoMessageType.Bazaar:
			StartCoroutine(Bazaar.GetCharacterBazaarList(delegate(BazaarExhibitingStatus res)
			{
				int num4 = 0;
				int num5 = 0;
				int num6 = 0;
				int num7 = 0;
				int num8 = 0;
				foreach (BazaarExhibitingElement element in res.Elements)
				{
					if (element.Status == E_BAZAAR_STATE.BAZAAR_STATE_PROCEEDS)
					{
						num5++;
						num6 += (int)element.Proceeds;
					}
					else if (element.Status == E_BAZAAR_STATE.BAZAAR_STATE_EXHIBITING)
					{
						if (element.RemainTime == 0)
						{
							num8++;
						}
						else
						{
							num4++;
							num7 += (int)(element.UnitPrice * element.Num);
						}
					}
				}
				AddRequestParam(AppInfoConditionType.Bazaar_BidNum, num5);
				AddRequestParam(AppInfoConditionType.Bazaar_BidPriceTotal, num6);
				AddRequestParam(AppInfoConditionType.Bazaar_ExhibitNum, num4);
				AddRequestParam(AppInfoConditionType.Bazaar_ExhibitPriceTotal, num7);
				AddRequestParam(AppInfoConditionType.Bazaar_TimeOverNum, num8);
				if (res.Elements.Count > 0)
				{
					BazaarExhibitingElement bazaarExhibitingElement = res.Elements[UnityEngine.Random.Range(0, res.Elements.Count)];
					AddRequestParam(AppInfoConditionType.Bazaar_ExhibitRndItemId, (int)bazaarExhibitingElement.Item.ItemID);
				}
				SetRoutine(Routine.GetTalk);
			}, null));
			break;
		case AppInfoMessageType.Craft:
			StartCoroutine(Craft.GetPawnStatus(delegate(CraftPawnStatusList res)
			{
				int num9 = 0;
				foreach (CraftPawnStatus status in res.Statuses)
				{
					if (status.RemainTime <= 0)
					{
						num9++;
					}
				}
				AddRequestParam(AppInfoConditionType.Craft_CompleteNum, num9);
				AddRequestParam(AppInfoConditionType.Craft_DoingNum, res.Statuses.Count);
				SetRoutine(Routine.GetTalk);
			}, null, CacheOption.OneMinute));
			break;
		case AppInfoMessageType.Mail_User:
			StartCoroutine(Mail.GetReceivedList(delegate(MailReceivedList res)
			{
				int num10 = 0;
				foreach (MailReceived element2 in res.Elements)
				{
					if (element2.State == 2)
					{
						num10++;
					}
				}
				AddRequestParam(AppInfoConditionType.Mail_Unread, num10);
				SetRoutine(Routine.GetTalk);
			}, null, MailType.User));
			break;
		case AppInfoMessageType.Mail_Ope:
			StartCoroutine(Mail.GetReceivedList(delegate(MailReceivedList res)
			{
				int num11 = 0;
				foreach (MailReceived element3 in res.Elements)
				{
					if (element3.State == 2)
					{
						num11++;
					}
				}
				AddRequestParam(AppInfoConditionType.Mail_Unread, num11);
				SetRoutine(Routine.GetTalk);
			}, null, MailType.Operation));
			break;
		case AppInfoMessageType.Gift:
			StartCoroutine(Gift.GetGiftList(delegate(CharacterGiftList res)
			{
				int num12 = 0;
				foreach (CharacterGift item in res.Gift)
				{
					foreach (CharacterGiftJem jem in item.Jems)
					{
						num12 += (int)jem.Value;
					}
				}
				AddRequestParam(AppInfoConditionType.Gift_BoxNum, res.Gift.Count);
				AddRequestParam(AppInfoConditionType.Gift_JemNum, num12);
				SetRoutine(Routine.GetTalk);
			}, null));
			break;
		}
	}

	private void Routine_GetTalk()
	{
		if (SubRoutineNo != 0)
		{
			return;
		}
		CharacterInfoPacket characterInfoPacket = new CharacterInfoPacket();
		characterInfoPacket.DataList = RequestParams;
		characterInfoPacket.MessageType = CurrentMessageType;
		StartCoroutine(TopInformation.PostChoiceInformation(delegate(TopInformationMessagePacket res)
		{
			if (string.IsNullOrEmpty(res.Message))
			{
				SetRoutine(Routine.Init);
			}
			if (!TalkInfo.SetText(res.Message, CurrentMessageType, RequestParams, TopicListResult))
			{
				SetRoutine(Routine.Init);
			}
			else
			{
				ThinkBaloon.gameObject.SetActive(value: false);
				if (CurrentMessageType != AppInfoMessageType.Greeting)
				{
					LightBaloon.alpha = 1f;
					LightBaloon.gameObject.SetActive(value: true);
					LightBaloon.FadeTo(0f, 0.3f, 1f, iTween.EaseType.linear, delegate
					{
						LightBaloon.gameObject.SetActive(value: false);
					});
				}
				SetRoutine(Routine.OpenWindow);
			}
		}, delegate
		{
			SetRoutine(Routine.Init);
		}, characterInfoPacket));
		SubRoutineNo = 1u;
	}

	private void Routine_OpenWindow()
	{
		if (SubRoutineNo == 0)
		{
			SubRoutineNo++;
			if (!OpenPage(delegate
			{
				SetRoutine(Routine.NpcTalk);
			}))
			{
				SetRoutine(Routine.Init);
			}
		}
	}

	private void Routine_NpcTalk()
	{
		if (!TextSending.IsEnd())
		{
			TextSending.Text.SetAllDirty();
		}
		else if (TalkInfo.IsEnd())
		{
			SetRoutine(Routine.CloseWait);
		}
		else if (RoutineDeltaTime >= NextPageWaitSecond)
		{
			RoutineDeltaTime = 0f;
			NextPage();
		}
	}

	private void Routine_CloseWindow()
	{
		DialogWindow.gameObject.SetActive(value: false);
		SetRoutine(Routine.Wait);
	}

	public void OnClickTalkWindow()
	{
		if (CurrentRoutine == Routine.NpcTalk)
		{
			if (IsAnimating())
			{
				SkipTextAnimation();
			}
			else if (!TalkInfo.IsEnd())
			{
				NextPage();
			}
		}
	}

	public void Routine_CloseWait()
	{
		if (SubRoutineNo == 0 && RoutineDeltaTime >= CloseWaitSecond)
		{
			SetNpcEmote(FootworkEmoteNo, 0f, delegate
			{
			});
			DialogWindow.localScale = Vector2.one;
			DialogWindow.ScaleTo(Vector2.zero, 0.3f, 0f, iTween.EaseType.easeInOutCirc, delegate
			{
				DialogWindow.gameObject.SetActive(value: true);
				TextSending.Text.text = string.Empty;
				SetRoutine(Routine.CloseWindow);
			});
			SubRoutineNo++;
		}
	}

	private void Routine_Wait()
	{
		if (RoutineDeltaTime >= NextTalkWaitSecond)
		{
			SetRoutine(Routine.Init);
		}
	}

	private void ShowText(string text, bool end)
	{
		TextSending.Text.text = text;
		TextSending.Initialize();
		NextPageIcon.gameObject.SetActive(value: false);
		NextPageIcon.gameObject.SetActive(!end);
	}

	private void SkipTextAnimation()
	{
		TextSending.FlushAll();
	}

	private bool IsAnimating()
	{
		return !TextSending.IsEnd();
	}

	private bool NextPage()
	{
		PageInfo page = TalkInfo.MoveNextPage();
		if (page == null)
		{
			return false;
		}
		if (page.EmoteNa != 0)
		{
			SetNpcEmote(page.EmoteNa, 0f, delegate
			{
				ShowText(page.Text, TalkInfo.IsEnd());
			});
		}
		else
		{
			ShowText(page.Text, TalkInfo.IsEnd());
		}
		return true;
	}

	private bool OpenPage(Action onComplete)
	{
		PageInfo page = TalkInfo.MoveNextPage();
		if (page == null)
		{
			return false;
		}
		if (page.EmoteNa != 0)
		{
			SetNpcEmote(page.EmoteNa, 1f, delegate
			{
				DialogWindow.localScale = Vector2.zero;
				DialogWindow.gameObject.SetActive(value: true);
				DialogWindow.ScaleTo(Vector2.one, 0.3f, 0f, iTween.EaseType.easeInOutCirc, delegate
				{
					ShowText(page.Text, TalkInfo.IsEnd());
					onComplete();
				});
			});
		}
		else
		{
			DialogWindow.localScale = Vector2.zero;
			DialogWindow.gameObject.SetActive(value: true);
			DialogWindow.ScaleTo(Vector2.one, 0.3f, 0f, iTween.EaseType.easeInOutCirc, delegate
			{
				ShowText(page.Text, TalkInfo.IsEnd());
				onComplete();
			});
		}
		return true;
	}
}
