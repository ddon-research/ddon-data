using System;
using Firebase.Analytics;
using UnityEngine;

public class AnalyticsManager : MonoBehaviour
{
	public enum Content
	{
		Prof_Status,
		Prof_ChangeIcon,
		Mail_Receive,
		Mail_Send,
		Inventory_Bag,
		Inventory_Warehouse,
		Inventory_Closet,
		Inventory_Post,
		Community_OnlineMember,
		Community_Friend,
		Clan_MemberList,
		Craft_Create,
		Craft_Status,
		Bazaar_Buy,
		Bazaar_Sell,
		Bazaar_Status,
		Other_Setting,
		Other_Tutorial,
		Other_ToWebRestania,
		Other_ToHelp,
		Other_ToSupport,
		Other_Logout,
		Other_ToOffical,
		Other_TOS,
		Other_Copyright
	}

	private void Awake()
	{
		FirebaseAnalytics.SetUserId(PlayerPerfManager.GetUUID());
	}

	private void OnApplicationPause(bool pause)
	{
		if (pause)
		{
		}
	}

	[EnumAction(typeof(Content))]
	public void LogSelectContent(int contentIndex)
	{
		FirebaseAnalytics.LogEvent(FirebaseAnalytics.EventSelectContent, "Name", Enum.GetName(typeof(Content), (Content)contentIndex));
	}

	public static void LogSelectContent(Content content)
	{
		FirebaseAnalytics.LogEvent(FirebaseAnalytics.EventSelectContent, "Name", Enum.GetName(typeof(Content), content));
	}
}
