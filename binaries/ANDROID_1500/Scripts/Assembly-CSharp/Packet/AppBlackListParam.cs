using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class AppBlackListParam
{
	public List<AppBlackList> BlackList = new List<AppBlackList>();
}
