using System;
using System.Collections;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.Networking;
using WebRequest;

public class CalendarUpdateInfoManager : SingletonMonoBehaviour<CalendarUpdateInfoManager>
{
	private CalendarUpdateInfoPackageDictionary package;

	private bool Caching;

	private bool NeedReload;

	public DateTime LastClanBoardUpdateTime { get; private set; }

	public uint PrivateTopicNum { get; private set; }

	public uint ClanTopicNum { get; private set; }

	public uint OfficialTopicNum { get; private set; }

	public uint PrivateTopicMax { get; private set; }

	public uint ClanTopicMax { get; private set; }

	public uint OfficialTopicMax { get; private set; }

	public bool IsCached { get; private set; }

	public bool IsClanMember { get; private set; }

	private void Start()
	{
		InitLoad();
	}

	private void Init()
	{
		IsCached = false;
		Caching = false;
		NeedReload = false;
		IsClanMember = false;
	}

	private void InitLoad()
	{
		CalendarUpdateInfoPackage calendarUpdateInfoPackage = PlayerPerfManager.GetCalendarReadTopic();
		if (calendarUpdateInfoPackage == null || calendarUpdateInfoPackage.OfficialReadList == null || calendarUpdateInfoPackage.ClanReadList == null)
		{
			CalendarUpdateInfoPackage calendarUpdateInfoPackage2 = new CalendarUpdateInfoPackage();
			calendarUpdateInfoPackage2.ClanReadList = new List<CalendarUpdateInfo>();
			calendarUpdateInfoPackage2.OfficialReadList = new List<CalendarUpdateInfo>();
			calendarUpdateInfoPackage2.ClanBoard = null;
			calendarUpdateInfoPackage = calendarUpdateInfoPackage2;
		}
		if (calendarUpdateInfoPackage.ClanBoard != null && (calendarUpdateInfoPackage.ClanBoard.Type == CalendarTopic.CALENDAR_TYPE.NONE || calendarUpdateInfoPackage.ClanBoard.UpdateDate == string.Empty || calendarUpdateInfoPackage.ClanBoard.TopicId == 0))
		{
			calendarUpdateInfoPackage.ClanBoard = null;
		}
		package = new CalendarUpdateInfoPackageDictionary
		{
			ClanBoard = calendarUpdateInfoPackage.ClanBoard
		};
		foreach (CalendarUpdateInfo clanRead in calendarUpdateInfoPackage.ClanReadList)
		{
			package.ClanReadList[clanRead.TopicId] = clanRead;
		}
		foreach (CalendarUpdateInfo officialRead in calendarUpdateInfoPackage.OfficialReadList)
		{
			package.OfficialReadList[officialRead.TopicId] = officialRead;
		}
		Init();
	}

	private IEnumerator CacheWait(Action onCallback = null)
	{
		if (onCallback != null)
		{
			while (!IsCached)
			{
				yield return new WaitForSeconds(0.05f);
			}
			onCallback();
		}
	}

	public bool IsExistClanBoard()
	{
		return package.ClanBoard != null;
	}

	public void Load(Action onCallBack = null)
	{
		StartCoroutine(CharacterCalendar.GetTopicUpdatedInfo(delegate(CalendarUpdateInfoParam result)
		{
			Check(result);
			PrivateTopicNum = result.PrivateTopicNum;
			ClanTopicNum = (uint)result.ClanList.Count;
			OfficialTopicNum = (uint)result.OfficialList.Count;
			PrivateTopicMax = result.PrivateTopicMax;
			ClanTopicMax = result.ClanTopicMax;
			OfficialTopicMax = result.OfficialTopicMax;
			IsClanMember = result.IsClanMember;
			IsCached = true;
			if (onCallBack != null)
			{
				onCallBack();
			}
			Caching = false;
		}, delegate(UnityWebRequest result)
		{
			AppUtility.ShowErr(result.downloadHandler.text, "CalendarTopic", IsPop: false);
		}, CacheOption.TenMinute));
	}

	private void Check(CalendarUpdateInfoParam pkg)
	{
		CalendarUpdateInfoPackageDictionary calendarUpdateInfoPackageDictionary = new CalendarUpdateInfoPackageDictionary();
		calendarUpdateInfoPackageDictionary.ClanReadList = new Dictionary<ulong, CalendarUpdateInfo>();
		calendarUpdateInfoPackageDictionary.OfficialReadList = new Dictionary<ulong, CalendarUpdateInfo>();
		calendarUpdateInfoPackageDictionary.ClanBoard = null;
		CalendarUpdateInfoPackageDictionary calendarUpdateInfoPackageDictionary2 = calendarUpdateInfoPackageDictionary;
		SelectData(package.OfficialReadList, pkg.OfficialList, calendarUpdateInfoPackageDictionary2.OfficialReadList);
		SelectData(package.ClanReadList, pkg.ClanList, calendarUpdateInfoPackageDictionary2.ClanReadList);
		if (pkg.ClanBoard.Type != 0)
		{
			LastClanBoardUpdateTime = DateTime.Parse(pkg.ClanBoard.UpdateDate);
		}
		calendarUpdateInfoPackageDictionary2.ClanBoard = package.ClanBoard;
		if (pkg.ClanBoard.Type == CalendarTopic.CALENDAR_TYPE.NONE || pkg.ClanBoard.TopicId == 0)
		{
			calendarUpdateInfoPackageDictionary2.ClanBoard = null;
		}
		package = calendarUpdateInfoPackageDictionary2;
	}

	private void SelectData(Dictionary<ulong, CalendarUpdateInfo> ReadList, List<CalendarUpdateInfo> UpdateList, Dictionary<ulong, CalendarUpdateInfo> NextReadList)
	{
		DateTime now = DateTime.Now;
		foreach (CalendarUpdateInfo Update in UpdateList)
		{
			if (ReadList.ContainsKey(Update.TopicId))
			{
				CalendarUpdateInfo calendarUpdateInfo = ReadList[Update.TopicId];
				CalendarUpdateInfo calendarUpdateInfo2 = Update;
				DateTime dateTime = DateTime.Parse(calendarUpdateInfo.UpdateDate);
				DateTime value = DateTime.Parse(calendarUpdateInfo2.UpdateDate);
				if (dateTime.CompareTo(value) >= 0)
				{
					NextReadList[Update.TopicId] = calendarUpdateInfo2;
					continue;
				}
			}
			DateTime dateTime2 = DateTime.Parse(Update.EndDate);
			if (Update.Type == CalendarTopic.CALENDAR_TYPE.EVENT && dateTime2.CompareTo(now) < 0)
			{
				NextReadList[Update.TopicId] = Update;
			}
		}
	}

	public void ReadTopic(CalendarUpdateInfo info)
	{
		switch (info.Type)
		{
		case CalendarTopic.CALENDAR_TYPE.CLAN:
			package.ClanReadList[info.TopicId] = info;
			break;
		case CalendarTopic.CALENDAR_TYPE.CLAN_MESSAGE_BOARD:
			package.ClanBoard = info;
			break;
		case CalendarTopic.CALENDAR_TYPE.EVENT:
			package.OfficialReadList[info.TopicId] = info;
			break;
		}
		CalendarUpdateInfoPackage calendarUpdateInfoPackage = new CalendarUpdateInfoPackage();
		calendarUpdateInfoPackage.ClanBoard = package.ClanBoard;
		CalendarUpdateInfoPackage calendarUpdateInfoPackage2 = calendarUpdateInfoPackage;
		foreach (KeyValuePair<ulong, CalendarUpdateInfo> clanRead in package.ClanReadList)
		{
			calendarUpdateInfoPackage2.ClanReadList.Add(clanRead.Value);
		}
		foreach (KeyValuePair<ulong, CalendarUpdateInfo> officialRead in package.OfficialReadList)
		{
			calendarUpdateInfoPackage2.OfficialReadList.Add(officialRead.Value);
		}
		PlayerPerfManager.SetCalendarReadTopic(calendarUpdateInfoPackage2);
	}

	public bool DidReadClanBoard()
	{
		if (!IsCached)
		{
			return false;
		}
		if (package.ClanBoard == null)
		{
			return false;
		}
		if (DateTime.Parse(package.ClanBoard.UpdateDate).CompareTo(LastClanBoardUpdateTime) == 0)
		{
			return true;
		}
		return false;
	}

	public bool DidReadTopic(CalendarTopic.CALENDAR_TYPE type, ulong topicId)
	{
		if (!IsCached)
		{
			return false;
		}
		switch (type)
		{
		case CalendarTopic.CALENDAR_TYPE.PRIVATE:
			return true;
		case CalendarTopic.CALENDAR_TYPE.CLAN:
			if (!package.ClanReadList.ContainsKey(topicId))
			{
				return false;
			}
			return true;
		case CalendarTopic.CALENDAR_TYPE.EVENT:
			if (!package.OfficialReadList.ContainsKey(topicId))
			{
				return false;
			}
			return true;
		case CalendarTopic.CALENDAR_TYPE.CLAN_MESSAGE_BOARD:
			return DidReadClanBoard();
		default:
			return false;
		}
	}

	public void UpdateUpdateInfo(Action onCallBack = null)
	{
		if (IsCached && !NeedReload)
		{
			onCallBack?.Invoke();
			return;
		}
		if (Caching)
		{
			StartCoroutine(CacheWait(onCallBack));
			return;
		}
		Caching = true;
		NeedReload = false;
		Load(onCallBack);
	}

	public void MarkReload()
	{
		CharacterCalendar.ClearCache_GetTopicUpdatedInfo();
		NeedReload = true;
	}

	public uint GetNewTopicNum(CalendarTopic.CALENDAR_TYPE type)
	{
		switch (type)
		{
		case CalendarTopic.CALENDAR_TYPE.CLAN:
		{
			int num2 = (int)ClanTopicNum - package.ClanReadList.Count;
			return (num2 >= 0) ? ((uint)num2) : 0u;
		}
		case CalendarTopic.CALENDAR_TYPE.EVENT:
		{
			int num = (int)OfficialTopicNum - package.OfficialReadList.Count;
			return (num >= 0) ? ((uint)num) : 0u;
		}
		default:
			return 0u;
		}
	}
}
