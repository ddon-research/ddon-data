using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class TutorialPathList
{
	public List<TutorialPath> Paths = new List<TutorialPath>();
}
