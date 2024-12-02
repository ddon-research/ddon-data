using UnityEngine;
using UnityEngine.UI;

public class CraftPawnSelectController : ViewController
{
	public enum SelectType
	{
		None = -1,
		MainPawn,
		SupportPawn
	}

	public enum SelectTargetType
	{
		Leader,
		Assist1,
		Assist2,
		Assist3
	}

	public SelectTargetType SelectTarget;

	public Toggle TabMainPawn;

	public Toggle TabSupportPawn;

	[SerializeField]
	private CraftPawnTableViewController TableView;

	[SerializeField]
	private RectTransform TableViewContent;

	private void OnEnable()
	{
		TabMainPawn.isOn = true;
		TabSupportPawn.isOn = false;
	}

	public void OnValueChangedMainPawnTab(bool b)
	{
		if (b)
		{
			StartCoroutine(TableView.LoadData());
			TableViewContent.anchoredPosition = new Vector2(TableViewContent.anchoredPosition.x, 0f);
		}
	}

	public void OnValueChangedSuportPawnTab(bool b)
	{
		if (b)
		{
			StartCoroutine(TableView.LoadData(SelectType.SupportPawn));
			TableViewContent.anchoredPosition = new Vector2(TableViewContent.anchoredPosition.x, 0f);
		}
	}

	public void DeicePawn(CraftpawnData pawn)
	{
		if (SelectTarget == SelectTargetType.Leader && !pawn.IsMyPawn)
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "サポートをリーダーにすることはできません");
			return;
		}
		if (!CanSelectPawn(pawn))
		{
			SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "既に選択中のポーンです");
			return;
		}
		switch (SelectTarget)
		{
		case SelectTargetType.Leader:
			SingletonMonoBehaviour<CraftManager>.Instance.Leader = pawn;
			break;
		case SelectTargetType.Assist1:
			SingletonMonoBehaviour<CraftManager>.Instance.Assist1 = pawn;
			break;
		case SelectTargetType.Assist2:
			SingletonMonoBehaviour<CraftManager>.Instance.Assist2 = pawn;
			break;
		case SelectTargetType.Assist3:
			SingletonMonoBehaviour<CraftManager>.Instance.Assist3 = pawn;
			break;
		}
		SingletonMonoBehaviour<NavigationViewController>.Instance.Pop();
	}

	public bool CanSelectPawn(CraftpawnData pawn)
	{
		if (SingletonMonoBehaviour<CraftManager>.Instance.Leader != null && SingletonMonoBehaviour<CraftManager>.Instance.Leader.MyPawnID == pawn.MyPawnID)
		{
			return false;
		}
		if (SingletonMonoBehaviour<CraftManager>.Instance.Assist1 != null && SingletonMonoBehaviour<CraftManager>.Instance.Assist1.MyPawnID == pawn.MyPawnID)
		{
			return false;
		}
		if (SingletonMonoBehaviour<CraftManager>.Instance.Assist2 != null && SingletonMonoBehaviour<CraftManager>.Instance.Assist2.MyPawnID == pawn.MyPawnID)
		{
			return false;
		}
		if (SingletonMonoBehaviour<CraftManager>.Instance.Assist3 != null && SingletonMonoBehaviour<CraftManager>.Instance.Assist3.MyPawnID == pawn.MyPawnID)
		{
			return false;
		}
		return true;
	}
}
