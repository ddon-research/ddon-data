using UnityEngine;

[CreateAssetMenu(menuName = "テキスト数字/テキスト数字")]
public class TextNumDataTable : ScriptableObject
{
	[SerializeField]
	public GameObject[] TextNumObjectList;

	public GameObject GetNum(uint num)
	{
		if (TextNumObjectList.Length > num)
		{
			return TextNumObjectList[num];
		}
		return null;
	}
}
