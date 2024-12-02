using System;
using UnityEngine;

public class HomeBGController : MonoBehaviour
{
	[SerializeField]
	private RectTransform HomeLayout;

	private RectTransform _rt;

	public RectTransform RT => _rt ?? (_rt = GetComponent<RectTransform>());

	public float NpcAlpha { get; set; }

	public float NpcMoving { get; set; }

	private void Update()
	{
		Vector2 anchoredPosition = HomeLayout.anchoredPosition;
		float num = RT.rect.width / (HomeLayout.rect.width * 2f);
		anchoredPosition.x *= num;
		RT.anchoredPosition = anchoredPosition;
		float num2 = Mathf.Abs(anchoredPosition.x) / 375f * 2f - 1f;
		num2 *= (float)Math.PI / 2f;
		NpcAlpha = Mathf.Cos(num2);
		NpcAlpha *= NpcAlpha;
		NpcMoving = Mathf.Sin(num2);
	}
}
