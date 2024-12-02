using System;

public class MailListData
{
	public enum ReadStatus
	{
		Read = 1,
		Unread
	}

	public uint CharacterIconID;

	public string SenderFirstName;

	public string SenderLastName;

	public string Title;

	public byte ItemReceived;

	public DateTime ReceivedAt;

	public ulong ID;

	public ReadStatus Status;
}
