using System.Collections.Generic;
using DDOAppMaster.Enum;
using UnityEngine;

public class SpriteManager : SingletonMonoBehaviour<SpriteManager>
{
	[SerializeField]
	private Sprite DefaultJobIcon;

	[SerializeField]
	private Sprite[] JobIcons;

	private Dictionary<uint, Sprite> JobIconDic = new Dictionary<uint, Sprite>();

	[SerializeField]
	private Sprite DefaultQesutIcon;

	[SerializeField]
	private Sprite[] QuestIcons;

	private Dictionary<QuestIconType, Sprite> QuestIconDic = new Dictionary<QuestIconType, Sprite>();

	private void Start()
	{
		for (uint num = 0u; num < JobIcons.Length; num++)
		{
			JobIconDic.Add(num + 1, JobIcons[num]);
		}
		QuestIconDic.Add(QuestIconType.MAIN, QuestIcons[0]);
		QuestIconDic.Add(QuestIconType.WORLD, QuestIcons[1]);
		QuestIconDic.Add(QuestIconType.PERSONAL, QuestIcons[2]);
		QuestIconDic.Add(QuestIconType.GRAND, QuestIcons[4]);
		QuestIconDic.Add(QuestIconType.EXTREME, QuestIcons[5]);
		QuestIconDic.Add(QuestIconType.SUBSTORY, QuestIcons[6]);
	}

	public Sprite GetJobIcon(uint id)
	{
		if (!JobIconDic.ContainsKey(id))
		{
			return DefaultJobIcon;
		}
		return JobIconDic[id];
	}

	public Sprite GetQuestIcon(QuestIconType type)
	{
		if (!QuestIconDic.ContainsKey(type))
		{
			return DefaultQesutIcon;
		}
		return QuestIconDic[type];
	}
}
