using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class MailReceivedDetail
{
	public MailText Text = new MailText();

	public List<MailItem> Items = new List<MailItem>();

	public List<MailGp> Gps = new List<MailGp>();

	public List<MailGpCourse> GpCourses = new List<MailGpCourse>();
}
