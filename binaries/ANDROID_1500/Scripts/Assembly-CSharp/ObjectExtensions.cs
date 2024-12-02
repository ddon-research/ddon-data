public static class ObjectExtensions
{
	public static string WithComma(this object self)
	{
		return $"{self:#,##0}";
	}
}
