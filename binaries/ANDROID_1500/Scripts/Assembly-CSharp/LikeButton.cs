using Packet;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

public class LikeButton : MonoBehaviour
{
	public GameObject ActiveImage;

	public Text LikeNumTxt;

	public void UpdateContent(bool IsLike, uint LikeNum, CalendarTopic.CALENDAR_TYPE type = CalendarTopic.CALENDAR_TYPE.NONE)
	{
		if (IsLike)
		{
			ActiveImage.SetActive(value: true);
		}
		else
		{
			ActiveImage.SetActive(value: false);
		}
		if (type != CalendarTopic.CALENDAR_TYPE.EVENT)
		{
			LikeNumTxt.text = LikeNum.ToString();
		}
		if ((bool)EventSystem.current)
		{
			EventSystem.current.SetSelectedGameObject(null);
		}
	}
}
