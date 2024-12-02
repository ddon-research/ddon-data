using System;

namespace Packet;

[Serializable]
public class JemInfo
{
	public CharacterJemList Jem = new CharacterJemList();

	public JemHistoryList AddHistory = new JemHistoryList();

	public JemHistoryList SubHistory = new JemHistoryList();
}
