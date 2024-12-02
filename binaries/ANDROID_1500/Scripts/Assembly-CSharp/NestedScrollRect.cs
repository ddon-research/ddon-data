using System;
using UnityEngine.EventSystems;
using UnityEngine.UI;

public class NestedScrollRect : ScrollRect
{
	private bool routeToParent;

	public override void OnInitializePotentialDrag(PointerEventData eventData)
	{
		base.transform.DoParentEventSystemHandler(delegate(IInitializePotentialDragHandler parent)
		{
			parent.OnInitializePotentialDrag(eventData);
		});
		base.OnInitializePotentialDrag(eventData);
	}

	public override void OnDrag(PointerEventData eventData)
	{
		if (routeToParent)
		{
			base.transform.DoParentEventSystemHandler(delegate(IDragHandler parent)
			{
				parent.OnDrag(eventData);
			});
		}
		else
		{
			base.OnDrag(eventData);
		}
	}

	public override void OnBeginDrag(PointerEventData eventData)
	{
		if (!base.horizontal && Math.Abs(eventData.delta.x) > Math.Abs(eventData.delta.y))
		{
			routeToParent = true;
		}
		else if (!base.vertical && Math.Abs(eventData.delta.x) < Math.Abs(eventData.delta.y))
		{
			routeToParent = true;
		}
		else
		{
			routeToParent = false;
		}
		if (routeToParent)
		{
			base.transform.DoParentEventSystemHandler(delegate(IBeginDragHandler parent)
			{
				parent.OnBeginDrag(eventData);
			});
		}
		else
		{
			base.OnBeginDrag(eventData);
		}
	}

	public override void OnEndDrag(PointerEventData eventData)
	{
		if (routeToParent)
		{
			base.transform.DoParentEventSystemHandler(delegate(IEndDragHandler parent)
			{
				parent.OnEndDrag(eventData);
			});
		}
		else
		{
			base.OnEndDrag(eventData);
		}
		routeToParent = false;
	}
}
