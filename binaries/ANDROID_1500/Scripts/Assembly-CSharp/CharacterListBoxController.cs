using System.Collections.Generic;
using Packet;
using UnityEngine;

public class CharacterListBoxController : ListBoxController<LoginCharacterList.ListElement>
{
	protected override void Setup(List<LoginCharacterList.ListElement> dataSources)
	{
		foreach (LoginCharacterList.ListElement character in SelectCharacterViewController.Instance.CharacterList.Characters)
		{
			dataSources.Add(character);
		}
		CreateElements();
	}

	public void OnClickElement(Object element)
	{
	}
}
