using System;

namespace Packet;

[Serializable]
public class JemHistory
{
	public JemActivitie Activitie;

	public int FreeValue;

	public int PayValue;

	public long Created;
}
