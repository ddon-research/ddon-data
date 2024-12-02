using UnityEngine;
using UnityEngine.UI;

public class BlacklistMemberSelector : TableViewCell<BlacklistTableViewController.BlackListData>
{
	public BlacklistTableViewController.BlackListData DataSource;

	[SerializeField]
	private Toggle OnlineToggle;

	[SerializeField]
	private CharacterIconController CharacterIcon;

	[SerializeField]
	private Text FirstName;

	[SerializeField]
	private Text LastName;

	[SerializeField]
	private Image JobIcon;

	[SerializeField]
	private Text JobLv;

	[SerializeField]
	private GameObject IsFriendIcon;

	[SerializeField]
	private GameObject IsClanMemberIcon;

	[SerializeField]
	private Toggle SelectedToggle;

	[SerializeField]
	private BlacklistTableViewController Controller;

	private void Start()
	{
	}

	public override void UpdateContent(BlacklistTableViewController.BlackListData data)
	{
		CharacterIcon.LoadImageAsync(data.data.CharIconId);
		FirstName.text = data.data.FirstName;
		LastName.text = data.data.LastName;
		JobIcon.sprite = SingletonMonoBehaviour<SpriteManager>.Instance.GetJobIcon(data.data.JobId);
		JobLv.text = data.data.JobLv.ToString();
		IsFriendIcon.SetActive(data.data.IsFriend);
		IsClanMemberIcon.SetActive(data.data.IsClanMember);
		OnlineToggle.isOn = data.data.IsOnline;
		DataSource = data;
		SelectedToggle.onValueChanged.RemoveAllListeners();
		if (data.IsBlock)
		{
			SelectedToggle.isOn = true;
		}
		else
		{
			SelectedToggle.isOn = false;
		}
		SelectedToggle.onValueChanged.AddListener(delegate
		{
			DataSource.IsBlock = SelectedToggle.isOn;
			Controller.ShowCountingBlockNum();
		});
	}

	public void SetFlag(bool IsBlock)
	{
		SelectedToggle.isOn = IsBlock;
	}

	public bool GetFlag()
	{
		return SelectedToggle.isOn;
	}
}
