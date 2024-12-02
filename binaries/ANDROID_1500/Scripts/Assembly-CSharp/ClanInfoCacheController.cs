using System;
using System.Collections;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.Networking;
using WebRequest;

public class ClanInfoCacheController : SingletonMonoBehaviour<ClanInfoCacheController>
{
	private Dictionary<uint, ClanMemberListElement> ClanInfoDic = new Dictionary<uint, ClanMemberListElement>();

	private bool Caching;

	private bool NeedReload;

	public bool IsCached { get; private set; }

	private void Start()
	{
		Init();
	}

	private void Init()
	{
		IsCached = false;
		Caching = false;
		NeedReload = false;
		ClanInfoDic.Clear();
	}

	public void OnEnable()
	{
	}

	private IEnumerator CacheWait(Action onCallback = null)
	{
		if (onCallback != null)
		{
			while (!IsCached)
			{
				yield return new WaitForSeconds(0.01f);
			}
			onCallback();
		}
	}

	public void UpdateClanMemberInfo(Action onCallBack = null)
	{
		if (ClanInfoDic.Count > 0 && IsCached && !NeedReload)
		{
			if (onCallBack != null)
			{
				onCallBack();
			}
			return;
		}
		if (Caching)
		{
			StartCoroutine(CacheWait(onCallBack));
			return;
		}
		Caching = true;
		NeedReload = false;
		IsCached = false;
		StartCoroutine(Clan.GetMember(delegate(ClanMemberList result)
		{
			ClanInfoDic.Clear();
			foreach (ClanMemberListElement member in result.Members)
			{
				ClanInfoDic[member.CharacterID] = member;
			}
			IsCached = true;
			if (onCallBack != null)
			{
				onCallBack();
			}
			Caching = false;
		}, delegate(UnityWebRequest result)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "エラー", "クランデータを取得できませんでした。\ncode:" + result);
		}, CacheOption.Nothing));
	}

	public void MarkReload()
	{
		NeedReload = true;
	}

	public ClanMemberListElement GetCharacterInfo(uint charId)
	{
		if (!IsCached)
		{
			UpdateClanMemberInfo();
			return null;
		}
		if (ClanInfoDic.ContainsKey(charId))
		{
			return ClanInfoDic[charId];
		}
		return null;
	}
}
