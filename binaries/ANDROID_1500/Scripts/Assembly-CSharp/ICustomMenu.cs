using System.Collections.Generic;

public interface ICustomMenu
{
	bool IsChanging { get; set; }

	void Deactivate();

	void SetContent(List<CustomMenuContentData> elements);
}
