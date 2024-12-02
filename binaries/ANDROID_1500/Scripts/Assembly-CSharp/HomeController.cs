using Packet;
using UnityEngine;
using UnityEngine.Analytics;
using UnityEngine.UI;

public class HomeController : MonoBehaviour
{
	[SerializeField]
	private CharacterIconController CharacterIcon;

	[SerializeField]
	private Text FirstNameText;

	[SerializeField]
	private Text LastNameText;

	[SerializeField]
	private Text JobLvText;

	[SerializeField]
	private Text ItemRankText;

	[SerializeField]
	private Text HPText;

	[SerializeField]
	private Text STText;

	public void UpdateContent(CharacterDataBase characterData)
	{
		CharacterIcon.LoadImageAsync(characterData.IconID);
		FirstNameText.text = characterData.FirstName;
		LastNameText.text = characterData.LastName;
		JobLvText.text = characterData.JobLv.ToString();
	}

	public void UpdateIcon(uint id)
	{
		CharacterIcon.LoadImageAsync(id);
	}

	public void OpenOfficalSite()
	{
		Analytics.CustomEvent("ClickToOpenOfficalSiteOnHome");
		Application.OpenURL("https://members.dd-on.jp/");
	}
}
