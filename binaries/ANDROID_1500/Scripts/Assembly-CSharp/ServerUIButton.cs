using Packet;
using UnityEngine;

public class ServerUIButton : MonoBehaviour
{
	public ServerUID Id;

	public void OnPush()
	{
		SingletonMonoBehaviour<ServerUIController>.Instance.OpenServerUI(Id);
	}
}
