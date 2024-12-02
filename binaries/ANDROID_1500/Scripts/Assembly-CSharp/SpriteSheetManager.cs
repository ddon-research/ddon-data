using System.Collections.Generic;
using UnityEngine;

public class SpriteSheetManager
{
	private static Dictionary<string, Dictionary<string, Sprite>> spriteSheets = new Dictionary<string, Dictionary<string, Sprite>>();

	public static void Load(string path)
	{
		if (!spriteSheets.ContainsKey(path))
		{
			spriteSheets.Add(path, new Dictionary<string, Sprite>());
		}
		SpriteListScriptableObject spriteListScriptableObject = Resources.Load<SpriteListScriptableObject>(path);
		Sprite[] sprite_list = spriteListScriptableObject.sprite_list;
		Sprite[] array = sprite_list;
		foreach (Sprite sprite in array)
		{
			if (!spriteSheets[path].ContainsKey(sprite.name))
			{
				spriteSheets[path].Add(sprite.name, sprite);
			}
		}
	}

	public static Sprite GetSpriteByName(string path, string name)
	{
		if (spriteSheets.ContainsKey(path) && spriteSheets[path].ContainsKey(name))
		{
			return spriteSheets[path][name];
		}
		return null;
	}
}
