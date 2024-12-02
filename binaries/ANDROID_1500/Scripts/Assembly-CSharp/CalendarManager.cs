using UnityEngine;

public class CalendarManager : SingletonMonoBehaviour<CalendarManager>
{
	[SerializeField]
	private TypedTopicListView _TypedTopicListView;

	[SerializeField]
	private CalendarController _CalendarController;

	[SerializeField]
	private DayListViewController _DayListView;

	[SerializeField]
	private TopicDetail _PrivateTopicDetail;

	[SerializeField]
	private ClanTopicDetail _ClanTopicDetail;

	[SerializeField]
	private TopicDetail _OfficialTopicDetail;

	[SerializeField]
	private CreateTopic _CreateTopic;

	[SerializeField]
	private EditTopic _EditTopic;

	[SerializeField]
	private BackImageController _BackImageController;

	[SerializeField]
	private CalendarMarkerFilter _MarkerFilter;

	public TypedTopicListView TypedTopicListView => _TypedTopicListView;

	public CalendarController CalendarController => _CalendarController;

	public DayListViewController DayListView => _DayListView;

	public TopicDetail PrivateTopicDetail => _PrivateTopicDetail;

	public ClanTopicDetail ClanTopicDetail => _ClanTopicDetail;

	public TopicDetail OfficialTopicDetail => _OfficialTopicDetail;

	public CreateTopic CreateTopic => _CreateTopic;

	public EditTopic EditTopic => _EditTopic;

	public BackImageController BackImageController => _BackImageController;

	public CalendarMarkerFilter MarkerFilter => _MarkerFilter;

	private void Start()
	{
		TypedTopicListView.FirstInitPrepare();
		DayListView.MyController.FirstInitPrepare();
		MarkerFilter.FilterInit();
		BackImageController.Init();
	}
}
