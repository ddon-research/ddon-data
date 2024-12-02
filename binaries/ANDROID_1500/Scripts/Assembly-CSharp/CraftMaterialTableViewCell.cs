using UnityEngine;
using UnityEngine.UI;
using Utility;

public class CraftMaterialTableViewCell : TableViewCell<CraftMaterialData>
{
	private Button ClickButton;

	[SerializeField]
	private new ItemIcon Icon;

	[SerializeField]
	private Text Name;

	[SerializeField]
	private Text NeedNumText;

	[SerializeField]
	private Text SelectedNumText;

	[SerializeField]
	private Image[] FillNumBGImages;

	private CraftMaterialData Data;

	[SerializeField]
	private ItemPicker ItemPicker;

	private void Start()
	{
		ClickButton = GetComponent<Button>();
		ClickButton.onClick.AddListener(OnClick);
	}

	private void Update()
	{
		if (Data == null)
		{
			return;
		}
		SelectedNumText.text = Data.SelectedNum.ToString();
		NeedNumText.text = (Data.NeedNum * SingletonMonoBehaviour<CraftManager>.Instance.CraftNum).ToString();
		if (FillNumBGImages != null)
		{
			Image[] fillNumBGImages = FillNumBGImages;
			foreach (Image image in fillNumBGImages)
			{
				image.gameObject.SetActive(Data.SelectedNum == Data.NeedNum * SingletonMonoBehaviour<CraftManager>.Instance.CraftNum);
			}
		}
	}

	public override void UpdateContent(CraftMaterialData materialData)
	{
		Data = materialData;
		Icon.Load(materialData.IconName, materialData.IconColorId);
		Name.text = materialData.ItemName;
		NeedNumText.text = materialData.NeedNum.ToString();
		SelectedNumText.text = materialData.SelectedNum.ToString();
		if (FillNumBGImages != null)
		{
			Image[] fillNumBGImages = FillNumBGImages;
			foreach (Image image in fillNumBGImages)
			{
				image.gameObject.SetActive(materialData.SelectedNum == materialData.NeedNum * SingletonMonoBehaviour<CraftManager>.Instance.CraftNum);
			}
		}
	}

	public void OnClick()
	{
		if (!SingletonMonoBehaviour<ProfileManager>.Instance.CanCraft())
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "本編でクラフトを解放していないため利用できません。\n解放後再ログインしてお試しください。");
			return;
		}
		ItemPicker.Push();
		ItemPicker.Setup(Data.ItemsId, Data.ItemName, Data.NeedNum * SingletonMonoBehaviour<CraftManager>.Instance.CraftNum, SingletonMonoBehaviour<CraftManager>.Instance.SetMaterials, SingletonMonoBehaviour<CraftManager>.Instance.GetMaterialNum);
	}
}
