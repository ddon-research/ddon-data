using UnityEngine;
using UnityEngine.UI;

public class ItemIcon : MonoBehaviour
{
	[SerializeField]
	private Image IconImage;

	[SerializeField]
	private Image ColorImage;

	private string IconName;

	private uint ColorId;

	private float timer;

	private static uint LoadingCount;

	private bool isLoading;

	private void Awake()
	{
	}

	private void Start()
	{
		IconImage.gameObject.SetActive(value: false);
		ColorImage.gameObject.SetActive(value: false);
	}

	private void Update()
	{
		if (!(timer > 0f))
		{
			return;
		}
		timer -= Time.deltaTime;
		if (!(timer <= 0f))
		{
			return;
		}
		StartCoroutine(ItemIconManager.LoadIcon(IconName, ColorId, delegate(Sprite texture)
		{
			if (texture == null)
			{
				string path2 = "Images/ico/ico_nowpri";
				texture = Resources.Load<Sprite>(path2);
			}
			IconImage.sprite = texture;
			IconImage.gameObject.SetActive(value: true);
			isLoading = false;
			if (LoadingCount != 0)
			{
				LoadingCount--;
			}
		}, delegate(Sprite texture)
		{
			if (texture == null)
			{
				string path = "Images/itembg/1";
				texture = Resources.Load<Sprite>(path);
			}
			ColorImage.sprite = texture;
			ColorImage.gameObject.SetActive(value: true);
		}));
	}

	private void OnDisable()
	{
		if (isLoading && LoadingCount != 0)
		{
			LoadingCount--;
		}
	}

	public void Load(string iconName, uint colorId)
	{
		IconName = iconName;
		ColorId = colorId;
		IconImage.gameObject.SetActive(value: false);
		ColorImage.gameObject.SetActive(value: false);
		if (!isLoading)
		{
			LoadingCount++;
		}
		isLoading = true;
		timer = (float)LoadingCount * 0.1f + 0.5f;
	}
}
