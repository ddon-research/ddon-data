using System;
using System.Collections.Generic;
using DDOAppMaster.Enum.TopInformation;

namespace Packet;

[Serializable]
public class CharacterInfoPacket
{
	public AppInfoMessageType MessageType;

	public List<TopInfomationKeyValuePair> DataList;
}
