struct MtObject
{
};

struct cResource
{
    char magicString[];
    u32 magicVersion;
};


struct MtSize_union_w_h
{
  s32 w;
  s32 h;
};

union MtSize_union
{
  MtSize_union_w_h _anon_0;
  u64 wh;
};

struct MtSize
{
  MtSize_union _anon_0;
};


union rGUI::HEADER::startFlowAdrs
{
  u32 startFlowIndex;
  nGUI::FLOW *startFlowAdrs;
};

union rGUI::HEADER::Animation
{
  u32 animationOffset;
  nGUI::ANIMATION *pAnimation;
};

union rGUI::HEADER::Sequence
{
  u32 sequenceOffset;
  nGUI::SEQUENCE *pSequence;
};

union rGUI::HEADER::Object
{
  u32 objectOffset;
  nGUI::OBJECT *pObject;
};

union rGUI::HEADER::ObjSequence
{
  u32 objSequenceOffset;
  nGUI::OBJ_SEQUENCE *pObjSequence;
};

union rGUI::HEADER::InitParam
{
  u32 initParamOffset;
  nGUI::INIT_PARAM *pInitParam;
};

union rGUI::HEADER::Param
{
  u32 paramOffset;
  nGUI::PARAM *pParam;
};

union rGUI::HEADER::Instance
{
  u32 instanceOffset;
  nGUI::INSTANCE *pInstance;
};

union rGUI::HEADER::Flow
{
  u32 flowOffset;
  nGUI::FLOW *pFlow;
};

union rGUI::HEADER::FlowProcess
{
  u32 flowProcessOffset;
  nGUI::FLOW_PROCESS *pFlowProcess;
};

union rGUI::HEADER::FlowInput
{
  u32 flowInputOffset;
  nGUI::FLOW_INPUT *pFlowInput;
};

union rGUI::HEADER::FlowSwitch
{
  u32 flowSwitchOffset;
  nGUI::FLOW_SWITCH *pFlowSwitch;
};

union rGUI::HEADER::FlowFunction
{
  u32 flowFunctionOffset;
  nGUI::FLOW_FUNCTION *pFlowFunction;
};

union rGUI::HEADER::Action
{
  u32 actionOffset;
  nGUI::ACTION *pAction;
};

union rGUI::HEADER::InputCondition
{
  u32 inputConditionOffset;
  nGUI::INPUT_CONDITION *pInputCondition;
};

union rGUI::HEADER::SwitchOperator
{
  u32 switchOperatorOffset;
  nGUI::SWITCH_OPERATOR *pSwitchOperator;
};

union rGUI::HEADER::SwitchCondition
{
  u32 switchConditionOffset;
  nGUI::SWITCH_CONDITION *pSwitchCondition;
};

union rGUI::HEADER::Variable
{
  u32 variableOffset;
  nGUI::VARIABLE *pVariable;
};

union rGUI::HEADER::Texture
{
  u32 textureOffset;
  nGUI::TEXTURE *pTexture;
};

union rGUI::HEADER::Font
{
  u32 fontOffset;
  nGUI::FONT *pFont;
};

union rGUI::HEADER::FontFilter
{
  u32 fontFilterOffset;
  void *pFontFilter;
};

union rGUI::HEADER::Message
{
  u32 messageOffset;
  nGUI::MESSAGE *pMessage;
};

union rGUI::HEADER::GUIResource
{
  u32 guiResourceOffset;
  nGUI::GUIRESOURCE *pGUIResource;
};

union rGUI::HEADER::GeneralResource
{
  u32 generalResourceOffset;
  nGUI::GENERALRESOURCE *pGeneralResource;
};

union rGUI::HEADER::CameraSetting
{
  u32 cameraSettingOffset;
  nGUI::CAMERA_SETTING *pCameraSetting;
};

union rGUI::HEADER::String
{
  u32 stringOffset;
  MT_STR pString;
};

union rGUI::HEADER::Key
{
  u32 keyOffset;
  nGUI::KEY *pKey;
};

union rGUI::HEADER::KeyValue8
{
  u32 keyValue8Offset;
  u8 *pKeyValue8;
};

union rGUI::HEADER::KeyValue32
{
  u32 keyValue32Offset;
  u8 *pKeyValue32;
};

union rGUI::HEADER::KeyValue128
{
  u32 keyValue128Offset;
  u8 *pKeyValue128;
};

union rGUI::HEADER::ExtendData
{
  u32 extendDataOffset;
  u8 *pExtendData;
};

union rGUI::HEADER::InstExeParam
{
  u32 instExeParamOffset;
  nGUI::PARAM *pInstExeParam;
};

union rGUI::HEADER::Vertex
{
  u32 vertexOffset;
  nGUI::VERTEX *pVertex;
};

struct rGUI::HEADER
{
  u32 magic;
  u32 version;
  u32 size;
  u32 attr;
  t64 updateTime;
  u32 instanceId;
  u32 flowId;
  u32 variableId;
  u32 startInstanceIndex;
  u32 animationNum;
  u32 sequenceNum;
  u32 objectNum;
  u32 objSequenceNum;
  u32 initParamNum;
  u32 paramNum;
  u32 keyNum;
  u32 instanceNum;
  u32 flowNum;
  u32 flowProcessNum;
  u32 flowInputNum;
  u32 flowSwitchNum;
  u32 flowFunctionNum;
  u32 actionNum;
  u32 inputConditionNum;
  u32 switchConditionNum;
  u32 switchOperatorNum;
  u32 variableNum;
  u32 textureNum;
  u32 fontNum;
  u32 fontFilterNum;
  u32 messageNum;
  u32 guiResourceNum;
  u32 generalResourceNum;
  u32 cameraSettingNum;
  u32 instExeParamNum;
  u32 vertexBufferSize;
  unsigned __int32 baseZ : 2;
  unsigned __int32 framerateMode : 1;
  unsigned __int32 languageSettingNo : 2;
  unsigned __int32 padding : 27;
  MtSize viewSize;
  rGUI::HEADER::startFlowAdrs _anon_0;
  rGUI::HEADER::Animation _anon_1;
  rGUI::HEADER::Sequence _anon_2;
  rGUI::HEADER::Object _anon_3;
  rGUI::HEADER::ObjSequence _anon_4;
  rGUI::HEADER::InitParam _anon_5;
  rGUI::HEADER::Param _anon_6;
  rGUI::HEADER::Instance _anon_7;
  rGUI::HEADER::Flow _anon_8;
  rGUI::HEADER::FlowProcess _anon_9;
  rGUI::HEADER::FlowInput _anon_10;
  rGUI::HEADER::FlowSwitch _anon_11;
  rGUI::HEADER::FlowFunction _anon_12;
  rGUI::HEADER::Action _anon_13;
  rGUI::HEADER::InputCondition _anon_14;
  rGUI::HEADER::SwitchOperator _anon_15;
  rGUI::HEADER::SwitchCondition _anon_16;
  rGUI::HEADER::Variable _anon_17;
  rGUI::HEADER::Texture _anon_18;
  rGUI::HEADER::Font _anon_19;
  rGUI::HEADER::FontFilter _anon_20;
  rGUI::HEADER::Message _anon_21;
  rGUI::HEADER::GUIResource _anon_22;
  rGUI::HEADER::GeneralResource _anon_23;
  rGUI::HEADER::CameraSetting _anon_24;
  rGUI::HEADER::String _anon_25;
  rGUI::HEADER::Key _anon_26;
  rGUI::HEADER::KeyValue8 _anon_27;
  rGUI::HEADER::KeyValue32 _anon_28;
  rGUI::HEADER::KeyValue128 _anon_29;
  rGUI::HEADER::ExtendData _anon_30;
  rGUI::HEADER::InstExeParam _anon_31;
  rGUI::HEADER::Vertex _anon_32;
};



bitfield rGUI_header_bits {
  mIsSetData : 1;
  mBaseZ : 2;
  mFramerateMode : 1;
  mLanguageSettingNo : 2;
  padding : 26;
};

struct rGUI : cResource
{
  rGUI::HEADER *mpHeader;
  u32 mAttr;
  rGUI_header_bits mHeaderBits;

  MtSize mViewSize;
  char mPreviewUnitName[];
  cGUIFontFilter **mpFontFilter;
  nDraw::VertexBuffer *mpVertexBuffer;
  rGUI::InstanceNeedObjectInfo *mpInstanceNeedObjectInfo;
  u32 mInstanceNullNeedNum;
  u32 mInstanceScissorMaskNeedNum;
  u32 mInstanceAnimationNeedNum;
  u32 mInstanceAnimVariableNeedNum;
  u32 mInstanceAnimControlNeedNum;
  u32 mGUIObjTextNeedNum;
  u32 mGUIObjMessageNeedNum;
  u32 mGUIObjChildAnimationRootNeedNum;
  u32 mGUIObjNullNeedNum;
  u32 mGUIObjTextureSetNeedNum;
  u32 mGUIObjTextureNeedNum;
  u32 mGUIObjPolygonNeedNum;
  u32 mGUIObjScissorMaskNeedNum;
  u32 mGUIObjColorAdjustNeedNum;
  u32 mGUIObjRootNeedNum;
  u32 mGUIVarIntNeedNum;
  u32 mGUIVarFloatNeedNum;
  u32 mCreateAnimationBufferSize;
  u32 mObjRootNeedSetObjectBufferSize;
};