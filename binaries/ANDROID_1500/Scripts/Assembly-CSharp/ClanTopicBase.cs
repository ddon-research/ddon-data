using System;
using System.Collections;
using Packet;
using UnityEngine;
using UnityEngine.UI;

public class ClanTopicBase : MonoBehaviour
{
	[SerializeField]
	private CharacterIconController IconController;

	[SerializeField]
	private Text CharacterName;

	[SerializeField]
	private Text PostDate;

	[SerializeField]
	private RegexHypertext Content;

	private IEnumerator routine;

	[SerializeField]
	private ClanRankIconController ClanIconController;

	[SerializeField]
	private AutoLayoutRebuilder MyRebuilder;

	private void Start()
	{
		Content.SetClickableByRegex("https?://[0-9a-zA-Z/:%#\\$&\\?\\(\\)~\\.=\\+\\-_]+", Color.cyan, delegate(string url)
		{
			Debug.Log(url);
			Application.OpenURL(url);
		});
	}

	public void UpdateContent(CalendarTopic topic)
	{
		uint iconId = 0u;
		string charName = "Former Member";
		Content.RemoveClickable();
		DateTime dateTime = DateTime.Parse(topic.Created);
		PostDate.text = dateTime.ToString("yyyy.MM.dd HH:mm");
		Content.text = topic.Content;
		Content.SetClickableByRegex("https?://[0-9a-zA-Z/:%#\\$&\\?\\(\\)~\\.=\\+\\-_]+", Color.cyan, delegate(string url)
		{
			Debug.Log(url);
			Application.OpenURL(url);
		});
		SingletonMonoBehaviour<ClanInfoCacheController>.Instance.UpdateClanMemberInfo(delegate
		{
			ClanMemberListElement characterInfo = SingletonMonoBehaviour<ClanInfoCacheController>.Instance.GetCharacterInfo(topic.CharacterId);
			ClanRankIconController.CLAN_RANK rank = ClanRankIconController.CLAN_RANK.MEMBER;
			if (characterInfo != null)
			{
				charName = characterInfo.FirstName + " " + characterInfo.LastName;
				iconId = characterInfo.IconID;
				rank = (ClanRankIconController.CLAN_RANK)characterInfo.MemberRank;
			}
			CharacterName.text = charName;
			IconController.LoadImageAsync(iconId, CharacterIconController.SIZE.CHAR_ICON_S);
			ClanIconController.LoadImageAsync(rank);
			MyRebuilder.MarkRebuild();
		});
	}

	private void OnEnable()
	{
		if (routine != null)
		{
			StartCoroutine(routine);
		}
	}
}
