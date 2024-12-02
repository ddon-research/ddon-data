using System;

namespace Packet;

[Serializable]
public class ErrorCodePacket
{
	public int ErrorCode;

	public string Message = string.Empty;

	public ErrorCodePacket(int error)
	{
		ErrorCode = error;
	}

	public ErrorCodePacket(int error, string msg)
	{
		ErrorCode = error;
		Message = msg;
	}
}
