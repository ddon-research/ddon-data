using System;

namespace Packet;

[Serializable]
public class Report
{
	public enum ERROR_CODE
	{
		ERROR_CODE_SUCCESS,
		ERROR_CODE_INVALID_DATA
	}

	public uint ReportedCharId;

	public Report(uint charId)
	{
		ReportedCharId = charId;
	}

	public Report()
	{
	}
}
