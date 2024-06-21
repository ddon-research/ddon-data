// local variable allocation has failed, the output may be wrong!
bool __fastcall cQuestTask::cQuestProcess::checkIsEnemyFound(
        cQuestTask::cQuestProcess *this,
        s32 stageNo,
        s32 groupNo,
        s32 setNo,
        s32 param04)
{
  sEnemyManager *enemyManagerReference; // rax
  u32 i; // r14d
  uDDOModel *ddoModel; // r13
  u32 mUnitParam; // ebx
  u32 UniqueIDStageId; // r12d
  u32 UniqueIDLayoutGroup; // r15d
  u32 QuestId; // eax
  nQuest::QUEST_ID v13; // rax OVERLAPPED
  nQuest::QUEST_ID *p_id; // rsi
  bool v15; // r15
  bool result; // al
  unsigned int uniqueId17; // ebx
  cContextInstance *contextInstanceFromUniqueId; // r14
  u32 questIdFromContextInstance19; // ebx
  u32 questIdFromQuestTaskId20; // ecx
  int flagIncrement21; // r15d
  unsigned int counter; // r13d
  unsigned int uniqueId23; // ebx
  cContextInstance *ContextInstFromUniqueId; // r14
  u32 questIdFromContextInstance25; // ebx
  u32 questIdFromQuestTask30; // ecx
  int setNoa; // [rsp+14h] [rbp-6Ch]
  u32 unitLayoutId; // [rsp+24h] [rbp-5Ch]
  nQuest::QUEST_ID id; // [rsp+30h] [rbp-50h] BYREF
  nQuest::QUEST_ID questId32; // [rsp+40h] [rbp-40h] BYREF
  __int64 v33; // [rsp+50h] [rbp-30h]

  v33 = **(_QWORD **)&_stack_chk_guard;
  if ( sAreaExt::isStage((const sAreaExt *)areaPointer)
    && LODWORD(areaPointer->mpArea[2][3].mSegmentName.value) != stageNo )
  {
    return 0;
  }
  setNoa = setNo;
  enemyManagerReference = enemyManagerPointer;
  if ( enemyManagerPointer->mBaseModelRefArray.mLength )
  {
    for ( i = 0; i < enemyManagerPointer->mBaseModelRefArray.mLength; ++i )
    {
      ddoModel = (uDDOModel *)enemyManagerReference->mBaseModelRefArray.mpArray[i];
      if ( ddoModel )
      {
        mUnitParam = ddoModel->mUnitParam;
        UniqueIDStageId = nLayout::getUniqueIDStageId(mUnitParam);
        UniqueIDLayoutGroup = nLayout::getUniqueIDLayoutGroup(mUnitParam);
        unitLayoutId = nLayout::getUniqueIDLayoutID(mUnitParam);
        if ( UniqueIDStageId == sAreaExt::convertStageId((const sAreaExt *)areaPointer, stageNo)
          && UniqueIDLayoutGroup == groupNo )
        {
          QuestId = uDDOModel::getQuestId(ddoModel);
          nQuest::QUEST_ID::QUEST_ID_0(&questId32, QuestId);
          v13 = cQuestTask::getQuestId((__int64)&id, this->mpParent);
          p_id = &id;
          v15 = nQuest::QUEST_ID::operator__(&questId32, v13);
          nQuest::QUEST_ID::_QUEST_ID(&id);
          nQuest::QUEST_ID::_QUEST_ID(&questId32);
          if ( v15 )
          {
            if ( (*((unsigned int (__fastcall **)(uDDOModel *))ddoModel->_vptr$MtObject + 188))(ddoModel) == 1 )
            {
              result = 1;
              if ( setNoa < 0 || unitLayoutId == setNoa )
                return result;
            }
            else if ( uDDOModel::isDead(ddoModel) )
            {
              result = 1;
              if ( unitLayoutId == setNoa || setNoa < 0 )
                return result;
            }
          }
        }
      }
      enemyManagerReference = enemyManagerPointer;
    }
  }
  if ( setNoa < 0 )
  {
    flagIncrement21 = 0;
    counter = 0;
    while ( 1 )
    {
      uniqueId23 = (8 * (unsigned __int16)sAreaExt::convertStageId((const sAreaExt *)areaPointer, stageNo)) & 0xFF8 | flagIncrement21 | (groupNo << 12) & 0x1FF000 | 0x80000002;
      ContextInstFromUniqueId = sContextManager::getContextInstFromUniqueId(contextManagerPointer, uniqueId23);
      if ( ContextInstFromUniqueId )
      {
        if ( sContextManager::isDeadEnemy(contextManagerPointer, uniqueId23) )
        {
          questIdFromContextInstance25 = cContextInterface::getQuestId(ContextInstFromUniqueId, 0LL);
          questIdFromQuestTask30 = cQuestTask::getQuestIdU32(this->mpParent);
          result = 1;
          if ( questIdFromContextInstance25 == questIdFromQuestTask30 )
            break;
        }
      }
      ++counter;
      flagIncrement21 += 0x200000;
      if ( counter >= 0x20 )
        return 0;
    }
  }
  else
  {
    uniqueId17 = (8 * (unsigned __int16)sAreaExt::convertStageId((const sAreaExt *)areaPointer, stageNo)) & 0xFF8 | (groupNo << 12) & 0x1FF000 | ((setNoa & 0x1F) << 21) | 0x80000002;
    contextInstanceFromUniqueId = sContextManager::getContextInstFromUniqueId(contextManagerPointer, uniqueId17);
    if ( !contextInstanceFromUniqueId )
      return 0;
    if ( !sContextManager::isDeadEnemy(contextManagerPointer, uniqueId17) )
      return 0;
    questIdFromContextInstance19 = cContextInterface::getQuestId(contextInstanceFromUniqueId, 0LL);
    questIdFromQuestTaskId20 = cQuestTask::getQuestIdU32(this->mpParent);
    result = 1;
    if ( questIdFromContextInstance19 != questIdFromQuestTaskId20 )
      return 0;
  }
  return result;
}