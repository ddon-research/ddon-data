using System;
using System.Collections.Generic;

namespace Packet;

[Serializable]
public class PlayerProfile
{
	public byte JobID;

	public string JobName;

	public uint ItemRank;

	public CharacterProfileData Profile = new CharacterProfileData();

	public List<JobLvData> JobInfo = new List<JobLvData>();

	public ClanBaseData Clan = new ClanBaseData();

	public ClanEmblemData ClanEmblem = new ClanEmblemData();
}
