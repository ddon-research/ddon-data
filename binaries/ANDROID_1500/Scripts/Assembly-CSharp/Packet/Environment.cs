using System;
using System.Collections.Generic;

namespace Packet;

public class Environment
{
	[Serializable]
	public class WeatherLoopInfo
	{
		public uint TypeID;

		public uint Sec;
	}

	public uint OriginalRealTimeYear;

	public uint OriginalRealTimeMon;

	public uint OriginalRealTimeMDay;

	public uint OriginalRealTimeHour;

	public uint OriginalGameTimeYear;

	public uint OriginalGameTimeMon;

	public uint OriginalGameTimeMDay;

	public uint OriginalGameTimeHour;

	public uint OriginalGameTimeMoon;

	public uint OriginalGameTimeWDay;

	public uint GameTimeOneDayMin;

	public uint MoonAgeLoopSec;

	public List<WeatherLoopInfo> WeatherLoops = new List<WeatherLoopInfo>();
}
