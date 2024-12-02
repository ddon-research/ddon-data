using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class LoginCharacterList
{
	[Serializable]
	public class ListElement
	{
		public uint CharacterID;

		public string FirstName;

		public string LastName;

		public ushort IconID;
	}

	public List<ListElement> Characters = new List<ListElement>();

	public string Token;
}
