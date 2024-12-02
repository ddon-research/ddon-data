using System.Collections.Generic;

public class MailSendManager : SingletonMonoBehaviour<MailSendManager>
{
	public enum AddrCategory
	{
		ClanMember,
		Friend
	}

	public AddrCategory SelectedAddrCategory { get; private set; }

	public Dictionary<uint, MemberListData> SelectedMemberList { get; private set; }

	private void Start()
	{
		SelectedAddrCategory = AddrCategory.ClanMember;
		SelectedMemberList = new Dictionary<uint, MemberListData>();
	}

	public bool SetAddrCategory(AddrCategory newCategory)
	{
		if (newCategory != SelectedAddrCategory)
		{
			SelectedAddrCategory = newCategory;
			SelectedMemberList.Clear();
			return true;
		}
		return false;
	}

	public Dictionary<uint, MemberListData> GetMemberList()
	{
		return SelectedMemberList;
	}

	public void CopyMemberList(Dictionary<uint, MemberListData> list)
	{
		SelectedMemberList.Clear();
		foreach (KeyValuePair<uint, MemberListData> item in list)
		{
			SelectedMemberList.Add(item.Key, item.Value);
		}
	}

	public bool IsSelectedMember(uint characterId)
	{
		return SelectedMemberList.ContainsKey(characterId);
	}

	public void ClearMemberList()
	{
		SelectedMemberList.Clear();
	}
}
