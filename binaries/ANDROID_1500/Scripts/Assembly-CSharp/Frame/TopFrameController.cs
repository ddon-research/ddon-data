using Packet;
using UnityEngine;
using UnityEngine.UI;

namespace Frame;

public class TopFrameController : MonoBehaviour
{
	[SerializeField]
	private Text FirstName;

	[SerializeField]
	private Text LastName;

	[SerializeField]
	private Text ClanName;

	[SerializeField]
	private Text Gold;

	[SerializeField]
	private Text Jem;

	[SerializeField]
	private CharacterIconController Icon;

	public void UpdateContent(CharacterDataBase data)
	{
		FirstName.text = data.FirstName;
		LastName.text = data.LastName;
		ClanName.text = data.ClanName;
		Gold.text = data.Gold.ToString("N0");
		Icon.LoadImageAsync(data.IconID);
	}

	public void UpdateIcon(uint id)
	{
		Icon.LoadImageAsync(id);
	}

	public void SetGold(uint gold)
	{
		Gold.text = gold.ToString("N0");
	}

	public void MoveToBuyJemPage()
	{
	}

	public void MoveToSelectIconPage()
	{
	}
}
