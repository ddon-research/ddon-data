struct CDataMasterInfo
{
  u32 m_unUniqueID; // => u64 on PC
  s8 m_cMasterIndex;
};

struct CPacket_S2C_MASTER_CHANGE_NOTICE : CPacket
{
  //u16 m_usError;
  //if(!m_usError)
      MtTypedArray<CDataMasterInfo> m_Info;
};

### To me it seems the error is no longer part of it?
### Since this is a notice, we can not easily figure out when or why this is sent.
### But here is another method that makes use of the same data struct (related to C2S_MASTER_THROW_REQ):

void __fastcall sSetManager::sendThrowMaster(sSetManager *this, u32 uniqueId, s32 index)
{
  MtCriticalSection *p_mCS; // rdi
  __int64 v6; // rdx
  cContextInstance *ContextInstFromUniqueId; // rax

  if ( (this->mThreadSafe || byte_2601638) && (p_mCS = &this->mCS, (unsigned int)scePthreadMutexLock(p_mCS))
    || (cNetGameServer::reqMasterThrow(
          *(cNetGameServer **)&qword_260AFF8[1].mContext[0].mInviteSessionInfo.mBinary.mBuffer[88],
          uniqueId,
          index),
        ContextInstFromUniqueId = sContextManager::getContextInstFromUniqueId(globalContextManagerPointer, uniqueId),
        *(_QWORD *)&uniqueId = 0xFFFFFFFFLL,
        cContextInterface::setMasterIndex(ContextInstFromUniqueId, -1), // -1 probably means "remove" "unset" in this case here
        this->mThreadSafe || byte_2601638)
    && (p_mCS = &this->mCS, (unsigned int)scePthreadMutexUnlock(&this->mCS)) )
  {
    abort(p_mCS, *(_QWORD *)&uniqueId, v6);
  }
}

void __fastcall cContextInterface::setMasterIndex(cContextInstance *pInst, s32 masterIndex)
{
  if ( pInst )
    pInst->mMasterIndex = masterIndex;
}

### Tracing back who is calling sendThrowMaster:

void __fastcall uDDOModel::throwMaster(uDDOModel *this, s32 index)
{
  uControl *mpCtrl; // rdi
  sSetManager *v4; // r15
  u32 UniqueId; // eax

  if ( this->mIsMaster && cContextInterface::getMasterChangeFlag(this->mContextInterface.mpContextInstance) )
  {
    mpCtrl = this->mpCtrl;
    if ( mpCtrl )
    {
      if ( (*((_DWORD *)&mpCtrl->cUnit + 4) & 7u) - 1 <= 1 )
        uControl::sendMasterParam(mpCtrl);
    }
    v4 = qword_25A57C0;
    UniqueId = cContextInterface::getUniqueId(
                 this->mContextInterface.mpContextInstance,
                 this->mContextInterface.mpContextCharacter);
    sSetManager::sendThrowMaster(v4, UniqueId, index);
  }
}

u32 __fastcall cContextInterface::getUniqueId(const cContextInstance *pInst, const cContextCharacter *pChara)
{
  u32 result; // eax

  result = 0;
  if ( pInst )
    return pInst->mUniqueId;
  return result;
}

### This means the uDDOModel's context instance and context character are used to generate the unique ID.

void __fastcall cContextInterface::setUniqueId(cContextInstance *pInst, cContextCharacter *pChara, u32 UniqueId)
{
  if ( pInst )
    pInst->mUniqueId = UniqueId;
}

### Luckily there is a basic setter as well, tracing that there are different use cases...

### Creating NPCs => uniqueId contains a mixture of layout ID, set info ID, stage number ###
uControlNpc *__fastcall cLayoutSetNpc::createUnitNpc(cLayoutSetNpc *this, const rLayout::SetInfo *psi)
[...]
v3 = nLayout::createUniqueID(U_NPC, this->mLayoutID._anon_0.mLayoutID >> 10, psi->mID, globalGamePointer->mStageNo) | 0x80000000;
v4 = sContextManager::searchContextNpc(globalContextManagerPointer, v3);
    if ( v4 )
    {
		cContextInterface::setUniqueId(v4, 0LL, v3);
[...]

### Creating a new context => uniqueId is provided ###
cContextInstance *__fastcall sContextManager::createContextInstance(
        sContextManager *this,
        u32 id,
        u32 uniqueId,
        s32 stageNo,
        s32 encountArea)
{
[...]
    for ( i = (cContextInstance *)this->mList[v6].mpTop; i; i = (cContextInstance *)i->mpNext )
    {
      *(_QWORD *)&id = 0LL;
      if ( cContextInterface::getUniqueId(i, 0LL) == uniqueId )
      {
        v8 = (*((__int64 (__fastcall **)(cContextInstance *))i->_vptr$MtObject + 5))(i);
        while ( *(MT_CTSTR *)(v8 + 8) != stru_25290A0.mName )
        {
          v8 = *(_QWORD *)(v8 + 32);
          if ( !v8 )
            goto LABEL_3;
        }
        return i;
      }
LABEL_3:
      ;
    }
    if ( (unsigned int)++v6 < 0xD )
      continue;
    break;
[...]
  cContextInterface::setUniqueId(i, 0LL, uniqueId);
  cContextInterface::setStageNo(i, 0LL, stageNo);
  cContextInterface::setMainEncountArea(i, encountArea);
  i->mIsValid |= 1u;
  return i;
}

### Creating a new context for enemies => uniqueId is provided, see below ###
uControlEnemy *__fastcall cFSMOrder::createControlEnemy(
        cFSMOrder *this,
        u32 enemyId,
        u32 uniqueId,
        const MtVector3 *pos,
        const MtVector3 *angle,
        MT_CTSTR filePath)
{
[...]
  ContextInstance = sContextManager::createContextInstance(
                      globalContextManagerPointer,
                      (enemyId - 149 > 0x38) | 8u,
                      uniqueId,
                      globalContextManagerPointer->mStageNo,
                      -1);
[...]

### Creating a new context for enemies => uniqueId is a mixture of group id, set id, inner ID 1F as constant, stage number ###
u32 __fastcall cFSMOrder::stateUpdateSetEnemy(cFSMOrder *this, MtObject *pParam, MtObject *pCaller)
{
[...]
        if ( EnemyId - 149 > 0x38 )
        {
          UniqueID_0 = nLayout::createUniqueID_0(
                         (nLayout::U_KIND)((char *)&qword_0 + 2),
                         v6->mGroupId,
                         v6->mSetId,
                         0x1Fu,
                         globalGamePointer->mStageNo);
          value = v6->mFsmPath.mFSMName.value;
          str = (const MT_CHAR *)value->str;
          if ( !value )
            str = &filePath;
          ControlEnemy = cFSMOrder::createControlEnemy(
                           (cFSMOrder *)((char *)&qword_0 + 2),
                           EnemyId,
                           UniqueID_0,
                           (const MtVector3 *)&angle.m[2],
                           (const MtVector3 *)&angle,
                           str);
          if ( ControlEnemy )
            ControlEnemy->mErosionMode = v6->mErosionLv;

### Creating a new context, another indirection layer, someone is setting up arrays, tracing...
void __fastcall sSetManager::sendRequestCreateContext(sSetManager *this)
{
[...]
  v2 = *this->mRequestCreateContextInfo.mpArray;
  id = (u32)v2[1]._vptr$MtObject;
[...]
  if ( cNetGameServer::reqGetSetContext(v6, id, v3, v4, v5, isLobby) )
    sContextManager::createContextInstance(globalContextManagerPointer, id, v3, v4, v5);
[...]

### This is where context instances can be queued ###
cContextInstance *__fastcall sContextManager::requestCreateContextInst(
        sContextManager *this,
        u32 id,
        u32 uniqueId,
        s32 encountArea)
{
[...]
          sSetManager::addRequestCreateContextInfo(globalContextManagerPointer, ida, uniqueId, encountArea),
          sSetManager::sendRequestCreateContext(globalContextManagerPointer),

### Going deep into the client framework during OM creation => uniqueId is made up of layoutID, setinfo ID, stage number,
cOmControl *__fastcall cLayoutSetOm::createUnitOm(cLayoutSetOm *this, const rLayout::SetInfo *psi)
{
[...]
        v12 = U_OM_SCR;
        if ( this->mLotType )
          v12 = U_OM;
        v13 = nLayout::createUniqueID_0(
                v12,
                this->mLayoutID._anon_0.mLayoutID >> 10,
                psi->mID,
                ((unsigned int)psi->mID >> 5) & 0x1F,
                globalGamePointer->mStageNo) | 0x80000000;
        if ( (OmParam->mUseComponent & 0x800) != 0 )
        {
          mpGroupParam = this->mpGroupParam;
          thisa = this;
          v15 = -1;
          if ( mpGroupParam->mKillAreaType )
            v15 = mpGroupParam->_anon_0.mDataCommon & 0x1FF;
          v16 = v13;
          v17 = sContextManager::searchContextOm(globalContextManagerPointer, v13);
          if ( !v17 )
          {
            sContextManager::requestCreateContextInst(globalContextManagerPointer, 0xBu, v16, v15);
[...]


Summary of call hierarchy (omitting lots of stuff) until set UniqueId is called:

sContextManager::requestCreateContextInst => sSetManager::sendRequestCreateContext => sContextManager::createContextInstance => cContextInterface::setUniqueId

sContextManager::requestCreateContextInst is called by ...
	cOmControl *__fastcall cQuestUnitGroup::createOm(cQuestUnitGroup *this, cQuestSet *pSet)
	uControlNpc *__fastcall cQuestUnitGroup::createNpc(cQuestUnitGroup *this, cQuestSet *pSet)
	uControlEnemy *__fastcall cLayoutSetEnemy::createUnitEnemy(cLayoutSetEnemy *this, rLayout::SetInfo *psi, const cLayoutPreset *preset, cGroupParam::EmSetInfo *pesi)
	uControlNpc *__fastcall cLayoutSetNpc::createUnitNpc(cLayoutSetNpc *this, const rLayout::SetInfo *psi)
	cOmControl *__fastcall cLayoutSetOm::createUnitOm(cLayoutSetOm *this, const rLayout::SetInfo *psi)

Thus the context unique ID encodes information from as many different cases as covered by above methods.