using System;
using System.Collections;
using System.Collections.Generic;
using Packet;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using WebRequest;

public class CommentItem : MonoBehaviour
{
	[SerializeField]
	private CharacterIconController IconController;

	[SerializeField]
	private Text CharacterName;

	[SerializeField]
	private Text PostDate;

	[SerializeField]
	private RegexHypertext Content;

	[SerializeField]
	private LikeButton Likebutton;

	[SerializeField]
	private GameObject myGameObject;

	[SerializeField]
	private Text CommentNo;

	[SerializeField]
	private ClanRankIconController ClanIconController;

	private IEnumerator routine;

	private TopicComment CommentData;

	[SerializeField]
	public CommentListViewer MyCommentListViewer;

	[SerializeField]
	private GameObject Border;

	[SerializeField]
	protected bool ReportIsPosting;

	protected object ReportthisLock = new object();

	[SerializeField]
	protected bool BlacklistIsPosting;

	protected object BlacklistthisLock = new object();

	[SerializeField]
	protected ImageGrid MyImageGrid;

	private void Start()
	{
		Content.SetClickableByRegex("https?://[0-9a-zA-Z/:%#\\$&\\?\\(\\)~\\.=\\+\\-_]+", Color.cyan, delegate(string url)
		{
			Debug.Log(url);
			Application.OpenURL(url);
		});
	}

	public void UpdateContent(TopicComment comment, CommentListViewer viewer)
	{
		CommentData = comment;
		uint id = 0u;
		string text = "Former Member";
		MyCommentListViewer = viewer;
		Content.RemoveClickable();
		DateTime dateTime = DateTime.Parse(comment.UpdatedAt);
		PostDate.text = dateTime.ToString("yyyy.MM.dd HH:mm");
		Content.text = comment.Content;
		int num = CalendarTopic.CountChar(comment.Content, '\n');
		if (num < 2)
		{
			int num2 = 2 - num;
			for (int i = 0; i < num2; i++)
			{
				Content.text += '\n';
			}
		}
		CommentNo.text = "No." + comment.No;
		Content.SetClickableByRegex("https?://[0-9a-zA-Z/:%#\\$&\\?\\(\\)~\\.=\\+\\-_]+", Color.cyan, delegate(string url)
		{
			Debug.Log(url);
			Application.OpenURL(url);
		});
		Likebutton.UpdateContent(comment.IsLiked, comment.LikeNum, CalendarTopic.CALENDAR_TYPE.CLAN);
		ClanMemberListElement characterInfo = SingletonMonoBehaviour<ClanInfoCacheController>.Instance.GetCharacterInfo(comment.CharacterId);
		ClanRankIconController.CLAN_RANK rank = ClanRankIconController.CLAN_RANK.MEMBER;
		if (characterInfo != null)
		{
			text = characterInfo.FirstName + " " + characterInfo.LastName;
			id = characterInfo.IconID;
			rank = (ClanRankIconController.CLAN_RANK)characterInfo.MemberRank;
		}
		CharacterName.text = text;
		IconController.LoadImageAsync(id, CharacterIconController.SIZE.CHAR_ICON_S);
		ClanIconController.LoadImageAsync(rank);
		MyImageGrid.UpdateContent(comment.ImageInfoList);
		Border.SetActive(value: true);
	}

	public void SetLast()
	{
		Border.SetActive(value: false);
	}

	private void OnEnable()
	{
		if (routine != null)
		{
			StartCoroutine(routine);
		}
		ReportIsPosting = false;
		BlacklistIsPosting = false;
	}

	public void LikeUpdate()
	{
		if (CommentData == null)
		{
			Debug.Log("CommentDataがnullです");
			return;
		}
		TopicComment postData = CommentData;
		postData.IsLiked = !postData.IsLiked;
		StartCoroutine(CharacterCalendar.PostComment(delegate
		{
			CommentData.IsLiked = postData.IsLiked;
			if (CommentData.IsLiked)
			{
				CommentData.LikeNum++;
			}
			else
			{
				CommentData.LikeNum--;
			}
			Likebutton.UpdateContent(CommentData.IsLiked, CommentData.LikeNum, CalendarTopic.CALENDAR_TYPE.CLAN);
			CharacterCalendar.ClearCache_GetCommentUInt64UInt32();
		}, delegate(UnityWebRequest result)
		{
			AppUtility.ShowErr(result.downloadHandler.text, "TopicComment");
		}, "like", postData, LoadingAnimation.Default));
	}

	public void ShowCommentPopUpMenu()
	{
		SingletonMonoBehaviour<ClanInfoCacheController>.Instance.UpdateClanMemberInfo(delegate
		{
			List<CustomMenuContentData> list = new List<CustomMenuContentData>();
			uint characterID = SingletonMonoBehaviour<ProfileManager>.Instance.CharacterData.CharacterID;
			ClanMemberListElement characterInfo = SingletonMonoBehaviour<ClanInfoCacheController>.Instance.GetCharacterInfo(characterID);
			if (characterID == CommentData.CharacterId)
			{
				list.Add(new CustomMenuContentData
				{
					Name = "コメントを編集",
					OnClick = delegate
					{
						EditComment();
					}
				});
			}
			else
			{
				list.Add(new CustomMenuContentData
				{
					Name = "コメントのテキストを範囲選択",
					OnClick = delegate
					{
						SelectComment();
					}
				});
			}
			if (characterID == CommentData.CharacterId)
			{
				list.Add(new CustomMenuContentData
				{
					Name = "コメントを削除",
					OnClick = delegate
					{
						DeleteComment(IsMaster: false);
					}
				});
			}
			else if (characterInfo.MemberRank == 1 || characterInfo.MemberRank == 2)
			{
				list.Add(new CustomMenuContentData
				{
					Name = "コメントを削除",
					OnClick = delegate
					{
						DeleteComment(IsMaster: true);
					}
				});
			}
			if (characterID != CommentData.CharacterId)
			{
				if (list.Count > 0)
				{
					list.Add(new CustomMenuContentData
					{
						IsBorder = true
					});
				}
				if (CommentData.IsReported)
				{
					list.Add(new CustomMenuContentData
					{
						TextColor = Color.gray,
						Name = "このコメントは通報済み",
						OnClick = delegate
						{
							SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "このコメントはすでに通報済みです。");
						}
					});
				}
				else
				{
					list.Add(new CustomMenuContentData
					{
						Name = "このコメントを通報する",
						OnClick = delegate
						{
							ReportTopic();
						}
					});
				}
				list.Add(new CustomMenuContentData
				{
					Name = "このキャラクターをブロックする",
					OnClick = delegate
					{
						BlockUser();
					}
				});
			}
			SingletonMonoBehaviour<PopUpMenuController>.Instance.Show(list);
		});
	}

	public void DeleteComment(bool IsMaster)
	{
		string body = "本当にコメントを削除しても\nよろしいですか？";
		if (IsMaster)
		{
			body = "クラン/サブマスター専用操作\n\nメンバーのコメントを\n本当に削除してもよろしいですか？";
		}
		SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK_Cancel, "コメント削除確認", body, delegate(ModalDialog.Result res)
		{
			if (res == ModalDialog.Result.OK)
			{
				StartCoroutine(CharacterCalendar.DeleteComment(delegate
				{
					SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "削除完了", "コメントを削除しました。", delegate(ModalDialog.Result dgRes)
					{
						if (dgRes == ModalDialog.Result.OK)
						{
							CharacterCalendar.ClearCache_GetCommentUInt64UInt32();
							MyCommentListViewer.Reload(NeedTopicListReload: true);
						}
					});
				}, delegate(UnityWebRequest result)
				{
					AppUtility.ShowErr(result.downloadHandler.text, "TopicComment", IsPop: false);
				}, CommentData.TopicId, CommentData.CommentId, LoadingAnimation.Default));
			}
		});
	}

	public void EditComment()
	{
		MyCommentListViewer.EditComment(CommentData, global::EditComment.CommentEditType.EDIT);
	}

	public void SelectComment()
	{
		MyCommentListViewer.EditComment(CommentData, global::EditComment.CommentEditType.SELECT);
	}

	public void ReportTopic()
	{
		SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK_Cancel, "確認", "このコメントを本当に通報しますか？", delegate(ModalDialog.Result res)
		{
			if (res == ModalDialog.Result.OK)
			{
				lock (ReportthisLock)
				{
					if (ReportIsPosting)
					{
						return;
					}
					ReportIsPosting = true;
				}
				ReportTopicInfo value = new ReportTopicInfo(CommentData.CharacterId, CommentData.TopicId, CommentData.CommentId, CommentData.Content);
				StartCoroutine(WebRequest.Report.PostTopic(delegate
				{
					SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "このコメントを通報しました。", delegate
					{
						CharacterCalendar.ClearCache_GetCommentUInt64UInt32();
						MyCommentListViewer.Reload();
					});
					MyCommentListViewer.Reload();
					ReportIsPosting = false;
				}, delegate(UnityWebRequest result)
				{
					AppUtility.ShowErr(result.downloadHandler.text, "ReportTopicInfo", IsPop: false);
					ReportIsPosting = false;
				}, value, LoadingAnimation.Default));
			}
		});
	}

	public void BlockUser()
	{
		SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK_Cancel, "確認", "このキャラクターを本当にブロックしますか？", delegate(ModalDialog.Result res)
		{
			if (res == ModalDialog.Result.OK)
			{
				lock (BlacklistthisLock)
				{
					if (BlacklistIsPosting)
					{
						return;
					}
					BlacklistIsPosting = true;
				}
				AppBlackListParam valueParam = new AppBlackListParam
				{
					BlackList = 
					{
						new Packet.AppBlackList(CommentData.CharacterId, isDeleted: false)
					}
				};
				StartCoroutine(WebRequest.AppBlackList.PostList(delegate
				{
					SingletonMonoBehaviour<ModalDialog>.Instance.Show(ModalDialog.Mode.OK, "確認", "このキャラクターをブロックしました。", delegate
					{
						CharacterCalendar.ClearCache_GetCommentUInt64UInt32();
						MyCommentListViewer.Reload();
						BlacklistIsPosting = false;
					});
				}, delegate(UnityWebRequest result)
				{
					AppUtility.ShowErr(result.downloadHandler.text, "AppBlackList", IsPop: false);
					BlacklistIsPosting = false;
				}, valueParam, LoadingAnimation.Default));
			}
		});
	}

	public void OpenProfile()
	{
		SingletonMonoBehaviour<ProfileManager>.Instance.OpenProfilePlayer(CommentData.CharacterId);
	}

	public void DestroyImage()
	{
		MyImageGrid.DestroyImages();
	}
}
