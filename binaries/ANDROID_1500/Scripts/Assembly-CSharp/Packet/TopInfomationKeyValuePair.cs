using System;
using DDOAppMaster.Enum.TopInformation;

namespace Packet;

[Serializable]
public class TopInfomationKeyValuePair
{
	public AppInfoConditionType Key;

	public int Value;

	public TopInfomationKeyValuePair(AppInfoConditionType key, int value)
	{
		Key = key;
		Value = value;
	}
}
