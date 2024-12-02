using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class GradationEffect : BaseMeshEffect
{
	public Color colorTop = Color.white;

	public Color colorBottom = Color.white;

	public override void ModifyMesh(VertexHelper vh)
	{
		if (IsActive())
		{
			List<UIVertex> list = new List<UIVertex>();
			vh.GetUIVertexStream(list);
			Gradation(list);
			vh.Clear();
			vh.AddUIVertexTriangleStream(list);
		}
	}

	private void Gradation(List<UIVertex> vertices)
	{
		for (int i = 0; i < vertices.Count; i++)
		{
			UIVertex value = vertices[i];
			value.color = ((i % 6 != 0 && i % 6 != 1 && i % 6 != 5) ? colorBottom : colorTop);
			vertices[i] = value;
		}
	}
}
