using System;
using System.Collections.Generic;
using Packet;

internal class GameDateTimeConverter
{
	private static DateTime UNIX_EPOCH = new DateTime(1970, 1, 1, 0, 0, 0, 0);

	private static uint REAL_TIME_ONE_DAY_MIN = 1440u;

	private static uint GAME_TIME_MOON_AGE = 30u;

	public static ulong OriginalGameTimeSec;

	public static ulong OriginalEarthTimeSec;

	public static uint GameTimeOneDayMin = 0u;

	public static uint MoonAgeLoopSec = 0u;

	public static uint OriginalMoonAge;

	public static List<Packet.Environment.WeatherLoopInfo> WeatherLoopInfos;

	public static ulong GetUnixTime(DateTime targetTime)
	{
		targetTime = targetTime.ToUniversalTime();
		return (ulong)targetTime.Subtract(UNIX_EPOCH).TotalSeconds;
	}

	public static DateTime FromUnixTime(long unixTime)
	{
		return UNIX_EPOCH.AddSeconds(unixTime).ToLocalTime();
	}

	public static void SetOriginalGameTime(ulong yy, ulong mm, ulong dd, ulong hh, ulong nn, ulong ss)
	{
		yy = yy * 360 * 24 * 60 * 60;
		mm = (mm - 1) * 30 * 24 * 60 * 60;
		dd = (dd - 1) * 24 * 60 * 60;
		hh = hh * 60 * 60;
		nn *= 60;
		ss = ss;
		OriginalGameTimeSec = yy + mm + dd + hh + nn + ss;
	}

	public static void SetOriginalEarthTime(int year, int mon, int day, int hour)
	{
		DateTime targetTime = new DateTime(year, mon + 1, day, hour, 0, 0);
		OriginalEarthTimeSec = GetUnixTime(targetTime);
	}

	public static GameDateTime GameSecToGameDateTime(ulong Sec)
	{
		GameDateTime gameDateTime = new GameDateTime();
		gameDateTime.Sec = Sec;
		gameDateTime.Week = (ushort)(Sec / 86400 % 8);
		gameDateTime.Moon = (ushort)((Sec + 172800) / 604800 % 12);
		gameDateTime.Yy = (ushort)(Sec / 31104000);
		Sec %= 31104000;
		gameDateTime.Mm = (ushort)(Sec / 2592000 + 1);
		Sec %= 2592000;
		gameDateTime.Dd = (ushort)(Sec / 86400 + 1);
		Sec %= 86400;
		gameDateTime.Hh = (ushort)(Sec / 3600);
		Sec %= 3600;
		gameDateTime.Nn = (ushort)(Sec / 60);
		Sec %= 60;
		gameDateTime.Ss = (ushort)Sec;
		return gameDateTime;
	}

	public static GameDateTime EarthToGame(DateTime Earth)
	{
		ulong unixTime = GetUnixTime(Earth);
		ulong sec = OriginalGameTimeSec + (unixTime - OriginalEarthTimeSec) * REAL_TIME_ONE_DAY_MIN / GameTimeOneDayMin;
		return GameSecToGameDateTime(sec);
	}

	public static uint GetEarthSecToWeather(DateTime time)
	{
		ulong unixTime = GetUnixTime(time);
		ulong num = 0uL;
		foreach (Packet.Environment.WeatherLoopInfo weatherLoopInfo in WeatherLoopInfos)
		{
			num += weatherLoopInfo.Sec;
		}
		if (num != 0)
		{
			ulong num2 = unixTime - OriginalEarthTimeSec;
			ulong num3 = num2 % num;
			foreach (Packet.Environment.WeatherLoopInfo weatherLoopInfo2 in WeatherLoopInfos)
			{
				if (num3 < weatherLoopInfo2.Sec)
				{
					return weatherLoopInfo2.TypeID;
				}
				num3 -= weatherLoopInfo2.Sec;
			}
		}
		return 1u;
	}

	public static uint GetEarthSecToMoonAge(DateTime time)
	{
		ulong unixTime = GetUnixTime(time);
		ulong num = GameTimeOneDayMin * 60;
		ulong originalEarthTimeSec = OriginalEarthTimeSec;
		ulong num2 = unixTime - originalEarthTimeSec;
		ulong num3 = (num2 + num / 2) / num * num;
		ulong num4 = MoonAgeLoopSec;
		ulong num5 = GAME_TIME_MOON_AGE;
		ulong num6 = num4 / num5;
		return (uint)((num3 / num6 + OriginalMoonAge) % num5);
	}
}
