using System;

namespace WebRequest;

public class CacheOption
{
	public TimeSpan Expire = new TimeSpan(0, 0, 0);

	public static CacheOption Default = new CacheOption();

	public static CacheOption Nothing = new CacheOption
	{
		IgnoreCache = true,
		NoCache = true
	};

	public static CacheOption ThreeSecond = new CacheOption
	{
		Expire = new TimeSpan(0, 0, 3)
	};

	public static CacheOption FiveSecond = new CacheOption
	{
		Expire = new TimeSpan(0, 0, 5)
	};

	public static CacheOption TenSecond = new CacheOption
	{
		Expire = new TimeSpan(0, 0, 10)
	};

	public static CacheOption HalfMinute = new CacheOption
	{
		Expire = new TimeSpan(0, 0, 30)
	};

	public static CacheOption OneMinute = new CacheOption
	{
		Expire = new TimeSpan(0, 1, 0)
	};

	public static CacheOption OneHour = new CacheOption
	{
		Expire = new TimeSpan(1, 0, 0)
	};

	public static CacheOption OneDay = new CacheOption
	{
		Expire = new TimeSpan(24, 0, 0)
	};

	public static CacheOption OneMonth = new CacheOption
	{
		Expire = new TimeSpan(720, 0, 0)
	};

	public static CacheOption TenMinute = new CacheOption
	{
		Expire = new TimeSpan(0, 10, 0)
	};

	public bool IgnoreCache { get; set; }

	public bool NoCache { get; set; }
}
