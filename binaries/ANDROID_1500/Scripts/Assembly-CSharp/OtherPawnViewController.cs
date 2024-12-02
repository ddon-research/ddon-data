using System.Collections;
using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

public class OtherPawnViewController : ViewControllerAfterLoad
{
	[SerializeField]
	private Text PawnName;

	[SerializeField]
	private Text PawnJobName;

	[SerializeField]
	private Image PawnJobIcon;

	[SerializeField]
	private Text PawnJobLevel;

	[SerializeField]
	private Image PawnSex;

	[SerializeField]
	private Text PawnItemLevel;

	[SerializeField]
	private Text ProfileParentName;

	[SerializeField]
	private Text ProfilePersonal;

	[SerializeField]
	private Text ProfileComment;

	[SerializeField]
	private ImageNumber CraftLevelNum;

	[SerializeField]
	private Text[] CraftParam;

	[SerializeField]
	private Text[] RentalParam;

	public uint CharacterId { get; set; }

	public uint PawnId { get; set; }

	private void Initialize()
	{
		PawnName.text = string.Empty;
		PawnJobName.text = string.Empty;
		PawnJobIcon.sprite = SingletonMonoBehaviour<SpriteManager>.Instance.GetJobIcon(0u);
		PawnJobLevel.text = string.Empty;
		PawnSex.sprite = SingletonMonoBehaviour<ProfileManager>.Instance.GetSexIcon(0u);
		PawnItemLevel.text = string.Empty;
		ProfileParentName.text = string.Empty;
		ProfilePersonal.text = string.Empty;
		ProfileComment.text = string.Empty;
		ProfileComment.text = string.Empty;
		CraftLevelNum.SetNumber(0u);
		CraftParam[0].text = string.Empty;
		CraftParam[1].text = string.Empty;
		CraftParam[2].text = string.Empty;
		CraftParam[3].text = string.Empty;
		CraftParam[4].text = string.Empty;
		RentalParam[0].text = string.Empty;
	}

	protected override IEnumerator LoadRoutine(ReqestResult result)
	{
		Initialize();
		yield return StartCoroutine(CharacterData.GetCharacterMainPawnProfile(delegate(MainPawnProfile res)
		{
			PawnName.text = res.Profile.Name;
			PawnJobName.text = res.JobName;
			PawnJobIcon.sprite = SingletonMonoBehaviour<SpriteManager>.Instance.GetJobIcon(res.JobID);
			PawnJobLevel.text = res.JobLv.ToString();
			PawnSex.sprite = SingletonMonoBehaviour<ProfileManager>.Instance.GetSexIcon(res.Profile.Sex);
			PawnItemLevel.text = res.ItemRank.ToString();
			ProfileParentName.text = res.Profile.ParentName;
			ProfilePersonal.text = res.Profile.Personal;
			ProfileComment.text = res.Profile.Comment;
			ProfileComment.text = res.Profile.Comment;
			CraftLevelNum.SetNumber(res.CraftLv);
			CraftParam[0].text = res.CraftSpeed.ToString();
			CraftParam[1].text = res.CraftCreateNum.ToString();
			CraftParam[2].text = res.CraftEquip.ToString();
			CraftParam[3].text = res.CraftCost.ToString();
			CraftParam[4].text = res.CraftQuality.ToString();
			RentalParam[0].text = res.RentalCost.ToString("N0");
			SingletonMonoBehaviour<ProfileManager>.Instance.SetStatusBase(res.Profile.Name, res.JobID, res.JobLv, res.ItemRank);
		}, delegate
		{
			result.isError = true;
		}, PawnId, CacheOption.OneMinute, LoadingAnimation.Default));
	}
}
