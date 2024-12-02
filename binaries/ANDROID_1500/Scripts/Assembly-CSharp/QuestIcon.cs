using DDOAppMaster.Enum;
using UnityEngine;
using UnityEngine.UI;

public class QuestIcon : MonoBehaviour
{
	[SerializeField]
	private Image[] Images;

	public void Setup(QuestIconType type)
	{
		Sprite questIcon = SingletonMonoBehaviour<SpriteManager>.Instance.GetQuestIcon(type);
		Image[] images = Images;
		foreach (Image image in images)
		{
			image.sprite = questIcon;
		}
	}
}
