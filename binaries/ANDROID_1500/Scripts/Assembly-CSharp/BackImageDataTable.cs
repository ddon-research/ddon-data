using UnityEngine;

[CreateAssetMenu(menuName = "カレンダー/カレンダー背景")]
public class BackImageDataTable : ScriptableObject
{
	[SerializeField]
	public string[] BackImageList;
}
