using Packet;
using UnityEngine;
using UnityEngine.UI;
using WebRequest;

[RequireComponent(typeof(ScrollRect))]
public class Mail_ListTableViewController : TableViewController<MailListData>
{
	public enum DataSourceType
	{
		Unread,
		FriendClan,
		Admin
	}

	[SerializeField]
	private DataSourceType SourceType;

	[SerializeField]
	private NavigationViewController navigationView;

	[SerializeField]
	private ViewController contentView;

	public void SetupType_Unread()
	{
		SourceType = DataSourceType.Unread;
		Title = "未読/見受け取りメール";
	}

	public void SetupType_FriendClan()
	{
		SourceType = DataSourceType.FriendClan;
		Title = "フレンド/クランメール";
	}

	public void SetupType_Admin()
	{
		SourceType = DataSourceType.Admin;
		Title = "運営からのメール";
	}

	private void LoadData()
	{
		TableData.Clear();
		StartCoroutine(Mail.GetReceivedList(mail_type: (SourceType != DataSourceType.FriendClan) ? MailType.Operation : MailType.User, onResult: delegate(MailReceivedList ret)
		{
			foreach (MailReceived element in ret.Elements)
			{
				MailListData mailListData = new MailListData();
				if (element.SenderCharacterId == 0)
				{
					mailListData.SenderFirstName = "DDO運営チーム";
					mailListData.CharacterIconID = 0u;
					mailListData.SenderFirstName = element.Name;
					mailListData.Title = element.Head;
				}
				else
				{
					mailListData.CharacterIconID = element.SenderCharacterIconId;
					mailListData.SenderFirstName = element.SenderCharacterFirstName;
					mailListData.SenderLastName = element.SenderCharacterLastName;
					mailListData.Title = element.Head;
				}
				mailListData.ID = element.Id;
				mailListData.ItemReceived = element.ItemReceived;
				mailListData.Status = ((element.State == 1) ? MailListData.ReadStatus.Read : MailListData.ReadStatus.Unread);
				mailListData.ReceivedAt = GameDateTimeConverter.FromUnixTime(element.Created);
				if (SourceType == DataSourceType.FriendClan)
				{
					if (element.SenderCharacterId != 0)
					{
						TableData.Add(mailListData);
					}
				}
				else if (SourceType == DataSourceType.Admin && element.SenderCharacterId == 0)
				{
					TableData.Add(mailListData);
				}
			}
			UpdateContents();
		}, onError: null, cacheOption: CacheOption.OneMinute, loadAnim: LoadingAnimation.Default));
	}

	protected override float CellHeightAtIndex(int index)
	{
		return 206f;
	}

	private void OnEnable()
	{
		LoadData();
	}

	public void OnPressCell(MainMenuTableViewCell cell)
	{
		if (navigationView != null)
		{
			navigationView.Push(contentView);
		}
	}
}
