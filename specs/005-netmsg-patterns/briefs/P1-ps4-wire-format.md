005 P1: PS4 02020005 wire format of the nNetMsg payloads

Question/objective (build: PS4_02020005): give the exact byte-level wire format, as a field list a
pattern author can transcribe, of the nNetMsg payloads carried by C2S_LOBBY_LOBBY_DATA_MSG_REQ
(3.3.16), S2C_LOBBY_LOBBY_DATA_MSG_NTC (3.4.16), C2S_PARTY_SEND_BINARY_MSG_NTC (6.25.16),
C2S_PARTY_SEND_BINARY_MSG_ALL_NTC (6.23.16) and their receive-side counterparts
(S2C_PARTY_RECV_BINARY_MSG*). All integers are big-endian (nNetwork::Coder).

Answer, from the PS4 database (names and types present):
1. Framing. Which functions build each packet's payload bytes on send and split them on receive
   (start from the callers of nNetMsgData::Head::serialize / Head::deserialize, nNetMsg::cNetMsgBase
   sendMessageCore/receiveMessageCore, nNetBase::cNetBase, cNetGameServer, sNetwork). What precedes
   stMsgHead: captured 3.3.16 payloads start `00000002 00000000 000007d0 40010015 00000000 ...`
   (a u32 2 before what looks like the Head). Captured 6.25.16 payloads look like several records:
   `00000000 80000000 28112a5a 4001 0002 | 00000000 80000000 28111ea2 01 0100 ...`. Are several
   messages batched per packet? Give the record header and how its length/count is known.
2. Every decoder, in read order, with types, conditions and counts: nNetMsgData::CtrlBase,
   CtrlAction::deserialize and all its helpers (popPos, popActionNo, receivePktCondition,
   receivePktCliffHang, receivePktEnemyClimb, receivePktShlShot, receiveMsgEnemyStatusCtrl,
   receiveMsgWallClimb, receiveMsgSlaveDamage, receiveMsgCatchRequest, receiveMsgActBow,
   receiveMsgMasterParam, receiveMsgOmRelease, receiveMsgShlStickParam, receiveMsgCustomSkillSync,
   receiveMsgSlaveDamageSv, receiveMsgShlRequestFromSlave), nNetMsgData::popNetPos/popNormalPos,
   GameBase, GameNormal (+ receiveMsgGamePawnMessage, receiveMsgGameSetEmDie,
   receiveMsgGameFreeMarker), GameEasy (+ PRTSet, PRTInfo, AreaRelease), SetBase, SetNormal (+
   ChangeMaster, MasterInfo, RequestCreateContext, CreateContext), ToolBase, ToolNormal, ToolEasy
   (+ DamageProfileStart, DamageProfileNode). Where the decoder reads a bit-packed or
   version-dependent field (isSameVer), say so.
3. The include-packet table read by nNetMsgData::createIncludePacketCtrl (PS4 0x1BECE20, 56 u32,
   index msgId-1): all 56 values, and the bit names if the DWARF/enum gives them.
4. Every cNetMsg* class DTI id (mMsgIdFull high 16 bits, e.g. 0x4001 cNetMsgCtrlAction,
   0x4100/0x4101 GameNormal/Easy, 0x4300 SetNormal, 0x4F00/0x4F01 ToolNormal/Easy) and every
   NET_MSG_ID enum per group with values. List any other cNetMsg* classes these packets can carry.

Owns: only the report `specs/005-netmsg-patterns/research/P1-ps4-wire-format.md` (Write it; no
other file). Others own everything else. Never touch: client/, packets/ data, the user's .i64
files, research/03040008/packets/.
Source boundary: the PS4 IDA 9.5 database through ida-mcp on your private copy
(`bash research/ida/private-copy.sh ps4 p1`); the Season 2 recompilation
`D:/ddon-data-s2/recompilation/src/DD_ONLINE/prog/` (nNetMsgData.h, cNetMsgBase.h, cNetBase.h) for
type declarations; captured samples via `xxd` on files under `packets/decrypted_raw/`
(e.g. `stream13-charcreation-marked.pcapng_tcp-stream-31/11527_C2S_LOBBY_LOBBY_DATA_MSG_REQ_*`).
Do not read the large `binaries/PS4_02020005/*.elf.c/.h` exports: use IDA.
Libraries: ida-mcp `execute_python` (ida_hexrays, ida_bytes, idautils); no own tooling.
Done: the report has (a) framing per packet with function names and VAs, (b) one field table per
decoder (order, type, name, condition), (c) the 56-entry table, (d) DTI ids and enums; each item
marked verified (read in IDA) or inferred; at least one captured 3.3.16 and one 6.25.16 payload
walked byte by byte with your format (the PS4 format may not fit Season 3 captures exactly: report
where it stops fitting, do not force it). Return a summary of at most 40 lines.
Stop: budget 60 min of work. Stop and report if ida-mcp will not open the copy.
Base: a9a2f2dea48. No commits.
