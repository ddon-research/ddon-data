#load "libs.csx"

public class ChatCommand : IChatCommand
{
    public override AccountStateType AccountState => AccountStateType.Admin;
    public override string CommandName => "flag";
    public override string HelpText => "usage: `/flag <set|clear> <WorldManageLayout|WorldManageQuest>` - Performs the operation using a quest flag";

    public Dictionary<QuestId, List<int>> data = new()
    {
        // [QuestId.Q70000001] = new()
        // {
        //     364,
        //     551,
        //     569,
        //     570,
        //     572,
        //     574,
        //     575,
        //     578,
        //     589,
        //     590,
        //     591,
        //     607,
        //     614,
        //     615,
        //     616,
        //     620,
        //     657,
        //     658,
        //     659,
        //     660,
        //     661,
        //     662, // Craft Officer (Sonia)
        //     663, // Vocation Arts (Archibald)
        //     703,
        //     704,
        //     707,
        //     718,
        //     727,
        //     748,
        //     760,
        //     764,
        //     765,
        //     766,
        //     768,
        //     770,
        //     771,
        //     772,
        //     777,
        //     779,
        //     784,
        //     786,
        //     787, // Myrmidons Pledge (The White Dragon)
        //     830,
        //     831,
        //     832,
        //     833,
        //     834,
        //     836,
        //     843,
        //     845,
        //     846,
        //     847,
        //     848,
        //     849,
        //     850,
        //     851,
        //     855,
        //     891,
        //     892,
        //     926, // Temple of purification south chamber
        //     927,
        //     932,
        // },
        // [QuestId.Q70001001] = new() {
        //     608,
        //     609,
        //     618,
        // },
        // [QuestId.Q70002001] = new() {
        //     576,
        //     781,
        //     856,
        //     925, // Gardnox Fortress
        // },
        // [QuestId.Q70003001] = new() {
        //     580,
        //     762,
        //     1062,
        // },
        // [QuestId.Q70004001] = new() {
        //     761,
        // },
        // [QuestId.Q70020001] = new() {
        //     1400,
        //     1409,
        //     1410,
        //     1411,
        //     1416,
        //     1418,
        //     1479, // Bertrand Area Info
        //     1490, // Arisen's Room
        //     1491,
        //     1523,
        //     1524,
        //     1525,
        //     1529,
        //     1531,
        //     1532,
        //     1538,
        //     1540,
        //     1541,
        //     1627,
        //     1672,
        //     1673,
        //     1675,
        //     1756,
        //     1757,
        //     1760,
        //     1761,
        //     1762,
        //     1763,
        // },
        // [QuestId.Q70021001] = new() {
        //     1433, // Bloodbane Isle Precipice
        //     1489, // Bloodbane Isle Summit
        //     1545,
        //     // 2439,
        //     // 2474,
        //     2477, // Play Point Shop (Renton)
        // },
        // [QuestId.Q70022001] = new() {
        //     // 1698, // Dana Gates
        //     // 1699,
        //     // 1703, // Kingal Canyon Border Checkpoint
        //     // 1709, // Musel Area Information
        //     // 1710, // Arthfael Area Information
        //     // 1711, // Razanailt Area Information
        //     // 1712, // Ciar Area Information
        //     // 1998, // Glyndwr Gates
        //     // 1999, // Western Gate of Morfaul
        //     // 2428,
        //     // 2432,
        //     // 2491,
        //     // 2682,
        //     // 2806,
        // },
        // [QuestId.Q70023001] = new() {
        //     // 1997, // Vegasa Corridor South
        //     // 2179,
        //     // 2180,
        //     // 2181,
        //     // // 2182, // Hollow of Beginnings Gathering Area
        //     // // 2183, // Valtable Hall
        //     // // 2184, // Valtable Hall Upper Area
        //     // 2245,
        //     // 2246,
        //     // 2400, // Vegasa Corridor East
        //     // 2402, // Vegasa Corridor West
        //     // 2564,
        // },
        // [QuestId.Q70030001] = new() {
        //     2814,
        //     2816,
        //     2913,
        //     2914,
        //     2915,
        //     2928,
        //     2930,
        //     2932,
        //     2946, // Vocation Emblem (Renton)
        //     3218,
        //     3219,
        //     3220,
        //     3221,
        //     3222,
        //     3224,
        //     3225,
        //     3226,
        //     3227,
        //     3229,
        //     3231,
        //     3236,
        //     3239,
        //     3240,
        //     3241,
        //     3301,
        //     3403,
        //     3414,
        //     3483,
        //     3508,
        //     3517,
        //     3518,
        //     3538,
        //     3539,
        //     3540,
        //     3578,
        //     3579,
        //     3592, // Custom Made Arms and Equipment Disassembly
        //     3604,
        //     3774,
        // },
        [QuestId.Q70031001] = new() {
            // 2923,
            // 2944,
            // 2952,
            // 2953,
            // 2956,
            // 3111, // Dark Path to Secret Spring
            // 3285,
            3286,
            // 3421,
            // 3519,
            // 3520,
            // 3580,
            // 3581,
            // 3603,
            // 4242,
            // 4243,
            // 4263,
            // 4412,
        },
        // [QuestId.Q70032001] = new() {
        //     4149,
        //     4179,
        //     4311,
        //     4312,
        //     4331,
        //     4402,
        //     4407,
        //     4408,
        //     4410,
        //     4449,
        //     4450,
        //     4451,
        //     4452,
        //     4471,
        //     4472,
        //     4473,
        //     4575,
        //     4580,
        //     4721,
        //     4734,
        //     4834,
        //     4835,
        //     4836,
        //     4845,
        //     4872,
        //     4978,
        //     4916,
        // },
        // [QuestId.Q70033001] = new() {
        //     4814,
        //     4914,
        //     4920,
        //     4921,
        //     4922,
        //     4923,
        //     4924,
        //     4940,
        //     4962,
        //     4965,
        //     4974,
        //     4975,
        //     4998,
        //     4999,
        //     5095,
        //     5097,
        //     5100,
        //     5190,
        //     5205,
        //     5208,
        //     5332,
        // },
        // [QuestId.Q70034001] = new() {
            // 5106,
            // 5184,
            // 5185,
            // 5186, // Dreed Castle Entrance
            // 5187, // Mergoda Security District
            // 5273,
            // 5274, // Synthesis of Dragon Abilities
            // 5286,
            // 5293,
            // 5306,
            // 5307,
            // 5308,
            // 5309,
            // 5310,
            // 5311,
            // 5313,
            // 5314,
            // 5315,
            // 5316,
            // 5357,
            // 5358,
            // 5359,
            // 5360,
            // 5378,
            // 5379,
            // 5380, // Dragon Armor Appraisal
            // 5399,
            // 5400,
            // 5403,
            // 5454,
        // },
    };


    public override void Execute(DdonGameServer server, string[] command, GameClient client, ChatMessage message, List<ChatResponse> responses)
    {
        if (command.Length < 2)
        {
            responses.Add(ChatResponse.CommandError(client, "No arguments provided"));
            return;
        }

        try
        {
            var action = command[0].ToLower();
            var type = command[1].ToLower();

            var baseQuest = QuestManager.GetQuestByQuestId(QuestId.WorldManageDebug);
            var questResultCommands = new List<CDataQuestCommand>();
            foreach (var (questId, flags) in data)
            {
                foreach(var flagNo in flags)
                {
                    switch (action)
                    {
                        case "set":
                            switch (type)
                            {
                                case "wml":
                                    questResultCommands.Add(QuestManager.ResultCommand.WorldManageLayoutFlagOn(flagNo, (int)questId));
                                    break;
                                case "wmq":
                                    questResultCommands.Add(QuestManager.ResultCommand.WorldManageQuestFlagOn(flagNo, (int)questId));
                                    break;
                                default:
                                    responses.Add(ChatResponse.CommandError(client, $"Unexpected flag type '{command[1]}'."));
                                    return;
                            }
                            break;
                        case "clear":
                            switch (type)
                            {
                                case "wml":
                                    questResultCommands.Add(QuestManager.ResultCommand.WorldManageLayoutFlagOff(flagNo, (int)questId));
                                    break;
                                case "wmq":
                                    questResultCommands.Add(QuestManager.ResultCommand.WorldManageQuestFlagOff(flagNo, (int)questId));
                                    break;
                                default:
                                    responses.Add(ChatResponse.CommandError(client, $"Unexpected flag type '{command[1]}'."));
                                    return;
                            }
                            break;
                        default:
                            responses.Add(ChatResponse.CommandError(client, $"Unknown action '{action}'."));
                            return;
                    }
                }
            }
            questResultCommands.Add(QuestManager.ResultCommand.RefreshOmKeyDisp());

            // Force the quest to execute
            S2CQuestQuestProgressNtc progressNtc = new S2CQuestQuestProgressNtc()
            {
                ProgressCharacterId = client.Character.CharacterId,
                QuestScheduleId = baseQuest.QuestScheduleId,
                QuestProcessStateList = new List<CDataQuestProcessState>()
                {
                    new CDataQuestProcessState()
                    {
                        ProcessNo = 0,
                        SequenceNo = 0,
                        BlockNo = 2,
                        ResultCommandList = questResultCommands
                    }
                }
            };
            client.Party.SendToAll(progressNtc);

            // Reset quest so a command can be sent again
            S2CQuestQuestProgressNtc resetNtc = new S2CQuestQuestProgressNtc()
            {
                ProgressCharacterId = client.Character.CharacterId,
                QuestScheduleId = baseQuest.QuestScheduleId,
                QuestProcessStateList = new List<CDataQuestProcessState>()
                {
                    new CDataQuestProcessState()
                    {
                        ProcessNo = 0,
                        SequenceNo = 0,
                        BlockNo = 1
                    }
                }
            };
            client.Party.SendToAll(resetNtc);
        }
        catch (Exception)
        {
            responses.Add(ChatResponse.CommandError(client, "Invalid Arguments"));
        }
    }
}

return new ChatCommand();
