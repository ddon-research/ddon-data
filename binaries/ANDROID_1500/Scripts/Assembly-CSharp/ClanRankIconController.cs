using System.Collections;
using UnityEngine;
using UnityEngine.UI;

[RequireComponent(typeof(Image))]
public class ClanRankIconController : MonoBehaviour
{
	public enum CLAN_RANK
	{
		MASTER = 1,
		SUBMASTER,
		MEMBER,
		APPRENTICE
	}

	private IEnumerator routine;

	private Image _MyImage;

	public Image MyImage
	{
		get
		{
			if (_MyImage == null)
			{
				_MyImage = GetComponent<Image>();
			}
			return _MyImage;
		}
		set
		{
			_MyImage = value;
		}
	}

	private void OnEnable()
	{
		if (routine != null)
		{
			StartCoroutine(routine);
		}
	}

	public void LoadImageAsync(CLAN_RANK rank)
	{
		MyImage.enabled = true;
		string text = "ico_clan_master";
		switch (rank)
		{
		case CLAN_RANK.MEMBER:
			MyImage.enabled = false;
			return;
		case CLAN_RANK.MASTER:
			text = "ico_clan_master";
			break;
		case CLAN_RANK.SUBMASTER:
			text = "ico_clan_leader";
			break;
		case CLAN_RANK.APPRENTICE:
			text = "ico_clan_beginner";
			break;
		}
		string filePath = "Images/ico/" + text;
		routine = LoadManager.LoadAsync(filePath, delegate(Sprite res)
		{
			if (MyImage != null)
			{
				MyImage.sprite = res;
			}
			routine = null;
		});
		if (base.gameObject.activeInHierarchy)
		{
			StartCoroutine(routine);
		}
	}
}
