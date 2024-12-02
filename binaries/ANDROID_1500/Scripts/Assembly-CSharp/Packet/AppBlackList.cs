using System;

namespace Packet;

[Serializable]
public class AppBlackList
{
	public enum ERROR_CODE
	{
		ERROR_CODE_SUCCESS
	}

	public uint RegisteredCharactersId;

	public bool IsDeleted;

	public AppBlackList(uint charId, bool isDeleted)
	{
		RegisteredCharactersId = charId;
		IsDeleted = isDeleted;
	}
}
