using UnityEngine;

public class NewClanBoardTopics : NewTopics
{
	public void UpdateContent(bool IsNew)
	{
		GameObject gameObject = NewNum.gameObject.transform.parent.gameObject;
		if (!IsNew)
		{
			gameObject.SetActive(value: false);
			return;
		}
		NewNum.text = "！";
		gameObject.SetActive(value: true);
	}
}
