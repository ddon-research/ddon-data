using Packet;

public class MemberListData
{
	public uint CharacterId;

	public uint CharIconId;

	public string FirstName;

	public string LastName;

	public uint JobId;

	public uint JobLv;

	public bool IsFriend;

	public bool IsClanMember;

	public bool IsOnline;

	public bool IsMine;

	public uint ClanMemberRank;

	public void SetFromPacket(CharacterMemberListElement elem)
	{
		CharacterId = elem.CharacterID;
		CharIconId = elem.IconID;
		FirstName = elem.FirstName;
		LastName = elem.LastName;
		JobId = elem.CurrentJobID;
		JobLv = elem.CurrentJobLv;
	}
}
