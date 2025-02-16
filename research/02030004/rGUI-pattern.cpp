#define f32 float
#define t64 u64

struct MtObject
{
};

struct cResource : MtObject
{
};

struct MtFloat3
{
  f32 x;
  f32 y;
  f32 z;
};

struct MtSize
{
    s32 w;
    s32 h;
};

struct MtHermiteCurve
{
  f32 x[8];
  f32 y[8];
};

enum nGUI_PARAM_TYPE : u8
{
  PARAM_TYPE_UNKNOWN = 0x0,
  PARAM_TYPE_INT = 0x1,
  PARAM_TYPE_FLOAT = 0x2,
  PARAM_TYPE_BOOL = 0x3,
  PARAM_TYPE_VECTOR = 0x4,
  PARAM_TYPE_RESOURCE = 0x5,
  PARAM_TYPE_STRING = 0x6,
  PARAM_TYPE_TEXTURE = 0x7,
  PARAM_TYPE_FONT = 0x8,
  PARAM_TYPE_MESSAGE = 0x9,
  PARAM_TYPE_VARIABLE = 0xA,
  PARAM_TYPE_ANIMATION = 0xB,
  PARAM_TYPE_EVENT = 0xC,
  PARAM_TYPE_GUIRESOURCE = 0xD,
  PARAM_TYPE_FONT_FILTER = 0xE,
  PARAM_TYPE_ANIMEVENT = 0xF,
  PARAM_TYPE_SEQUENCE = 0x10,
  PARAM_TYPE_INIT_BOOL = 0x11,
  PARAM_TYPE_INIT_INT = 0x12,
  PARAM_TYPE_GENERALRESOURCE = 0x13,
};

enum nGUI_FLOW_TYPE : s32
{
  FLOW_TYPE_START = 0x0,
  FLOW_TYPE_END = 0x1,
  FLOW_TYPE_PROCESS = 0x2,
  FLOW_TYPE_INPUT = 0x3,
  FLOW_TYPE_SWITCH = 0x4,
  FLOW_TYPE_FUNCTION = 0x5,
  FLOW_TYPE_NUM = 0x6,
};

enum nGUI_END_CONDITION_TYPE : s32
{
  EC_FLOW_ANIMATION_END = 0x0,
  EC_FRAME_COUNT = 0x1,
  EC_INFINITE = 0x2,
  EC_CHANGE_VARIABLE = 0x3,
  EC_ANIMATION_END = 0x4,
};

enum nGUI_LANGUAGE_SETTING : s32
{
  LANGUAGE_SETTING0 = 0x0,
  LANGUAGE_SETTING1 = 0x1,
  LANGUAGE_SETTING2 = 0x2,
};

enum nGUI_FRAMERATE_MODE : s32
{
  FRAMERATE_60FPS = 0x0,
  FRAMERATE_30FPS = 0x1,
};

enum nGUI_BASE_Z : s32
{
  BASE_Z_ORIGIN = 0x0,
  BASE_Z_PARALLAX_ZERO = 0x1,
  BASE_Z_NEAR_CLIP = 0x2,
};

enum nGUI_KEY_MODE : s32
{
  MODE_CONSTANT = 0x0,
  MODE_OFFSET = 0x1,
  MODE_TRIGGER = 0x2,
  MODE_LINEAR = 0x3,
  MODE_OFFSET_F = 0x4,
  MODE_HERMITE = 0x5,
  MODE_EASEIN = 0x6,
  MODE_EASEOUT = 0x7,
  MODE_HERMITE2 = 0x8,
  MODE_NUM = 0x9,
  MODE_SUMMARY = 0xA,
  MODE_DEFAULT = 0xB,
};

enum nGUI_TEXTURE_RTYPE : s32
{
  RTYPE_TEXTURE = 0x0,
  RTYPE_RENDERTARGET = 0x1,
};

bitfield rGUI_HEADER_BITS
{
nGUI_BASE_Z baseZ:
    2;
nGUI_FRAMERATE_MODE framerateMode:
    1;
nGUI_LANGUAGE_SETTING languageSettingNo:
    2;
paddin:
    27;
};

struct rGUI_InstanceNeedObjectInfo
{
    u32 objTextNeedNum;
    u32 objMessageNeedNum;
    u32 objChildAnimationRootNeedNum;
    u32 objNullNeedNum;
    u32 objTextureSetNeedNum;
    u32 objTextureNeedNum;
    u32 objPolygonNeedNum;
    u32 objScissorMaskNeedNum;
    u32 objColorAdjustNeedNum;
    u32 objRootNeedNum;
    u32 createAnimationBufferSize;
    u32 objRootNeedSetObjectBufferSize;
};

enum MtDTI : u32 {
    cGUIInstNull = 1100687399,
    cGUIInstAnimation = 497711579,
    cGUIVarInt = 1022169983,
    cGUIFontFilterGradationOverlay = 1998668322,
    rTexture = 606035435,
    cGUIObjRoot = 473969240,
    cGUIObjNull = 796866380,
    cGUIObjTexture = 459477923,
    cGUIObjPolygon = 1587625923,
    cGUIObjMessage = 800599726,
    cGUIObjColorAdjust = 122938906,
    cGUIObjTextureSet = 1332881660,
    cGUIObjTextureRef = 1024013187,
};

struct nGUI_INSTANCE
{
  u32 id;
  u32 attr;
  u32 nextIndex;
  u32 childIndex;
  u32 initParamNum;
  u32 nameOffset;
  char pName[] @ mpHeader.stringOffset+nameOffset;
  MtDTI dtiId;
  // const MtDTI *pDti;
  u32 initParamIndex;
  //nGUI::INIT_PARAM *pInitParam;
  u32 extendDataOffset;
  //void *pExtendData;
};

struct nGUI_ANIMATION
{
  u32 id;
  u16 objectNum;
  u16 sequenceNum;
  u16 drawableObjectNum;
  u16 animateParamNum;
  u32 objectIndex;
  u32 nameOffset;
  char pName[] @ mpHeader.stringOffset+nameOffset;
  u32 sequenceIndex;
  //nGUI::SEQUENCE *pSequence;
};

struct nGUI_MESSAGE
{
  u32 id;
  //void *pMessage;//void*

  u32 pathOffset;
  char path[] @ mpHeader.stringOffset+pathOffset;
};

struct nGUI_FLOW
{
  u32 id;
  nGUI_FLOW_TYPE type;
  u32 attr;

  u32 nameOffset;
  char pName[] @ mpHeader.stringOffset+nameOffset;

  u32 processIndex;
    //u32 nextIndex;
    //nGUI::FLOW *nextAdrs;
    //u32 inputIndex;
    //nGUI::FLOW_INPUT *inputAdrs;
    //u32 switchIndex;
    //nGUI::FLOW_SWITCH *switchAdrs
    //u32 functionIndex;
    //nGUI::FLOW_FUNCTION *functionAdrs;
};

struct nGUI_SEQUENCE
{
  u32 id;
  u32 frameCount;

  u32 nameOffset;
  char pName[] @ mpHeader.stringOffset+nameOffset;
};

struct nGUI_OBJ_SEQUENCE
{
  u16 attr;
  u8 initParamNum;
  u8 paramNum;
  u16 loopStart;
  u16 frameCount;

  u32 initParamIndex;
  //nGUI::INIT_PARAM *pInitParam;

  u32 paramIndex;
  //nGUI::PARAM *pParam;
};

bitfield nGUI_FLOW_PROCESS_BITS {
  isLoop : 8;
  loopStart : 24;
};

struct nGUI_FLOW_PROCESS
{
  nGUI_FLOW_PROCESS_BITS bits;
  u32 totalFrame;
  u32 paramNum;
  u32 paramIndex;
  u32 actionNum;
  nGUI_END_CONDITION_TYPE endConditionType;
  u32 endConditionParam;
    
  u32 nextIndex;
  //nGUI::FLOW *nextAdrs;
  
  u32 actionIndex;
  //nGUI::ACTION *actionAdrs;
};

struct nGUI_VERTEX
{
  f32 x;
  f32 y;
  f32 z;
  u32 color;
  f32 u;
  f32 v;
};

bitfield nGUI_KEY_BITS {
  frame : 24;
  nGUI_KEY_MODE mode : 8;
};

struct nGUI_KEY
{
  nGUI_KEY_BITS bits;
  
  u32 curveOffset;
  //MtHermiteCurve *pCurve;
};

bitfield nGUI_PARAM_BITS {
  nGUI_PARAM_TYPE paramType : 8;
  keyNum : 9;
  reserved : 15;
};

struct nGUI_PROP_SETTER
{
  u16 type;
  u16 callNo;
  //MT_CTSTR name;
  //MT_MFUNC func;
};

struct nGUI_PARAM
{
  nGUI_PARAM_BITS bits;
  nGUI_PROP_SETTER Func;
  //const nGUI::PROP_SETTER *pFunc;
  u32 parentId;
    
  u32 propNameOffset;
  char propName[] @ mpHeader.stringOffset+propNameOffset;
  
  u32 frameOffset;
  nGUI_KEY keyFrame[bits.keyNum] @ mpHeader.keyOffset+frameOffset;//*
      
  u32 valueOffset;
  // TODO: maybe decide on size based on param type?
  u8 keyValue[bits.keyNum] @ mpHeader.keyValue8Offset+valueOffset;//*
};

bitfield nGUI_INIT_PARAM_BITS {
  nGUI_PARAM_TYPE paramType : 8;
  reserved : 24;
};

union nGUI_INIT_PARAM_value{
    u32 valueOffset;
    u8 pValue;//*
    bool bValue;
    s32 iValue;
};

struct nGUI_INIT_PARAM
{
  nGUI_INIT_PARAM_BITS bits;
  nGUI_PROP_SETTER Func;
  //const nGUI_PROP_SETTER *pFunc;

  u32 propNameOffset;
  char propName[] @ mpHeader.stringOffset+propNameOffset;

  nGUI_INIT_PARAM_value value;
};

struct nGUI_CAMERA_SETTING
{
  u32 id;
  f32 nearPlane;
  f32 farPlane;
  MtFloat3 cameraPos;
  MtFloat3 targetPos;
  MtFloat3 cameraUp;

  u32 nameOffset;
  char pName[] @ mpHeader.stringOffset+nameOffset;
};

bitfield nGUI_VARIABLE_BITS {
  isLoopValue : 1;
  reserved : 31;
};

  union nGUI_VARIABLE_init
  {
    s32 iInit;
    f32 fInit;
  };
  union nGUI_VARIABLE_min
  {
    s32 iMin;
    f32 fMin;
  };
  union nGUI_VARIABLE_max
  {
    s32 iMax;
    f32 fMax;
  };

struct nGUI_VARIABLE
{
  u32 id;
  nGUI_VARIABLE_BITS bits;
  
  u32 nameOffset;
  char pName[] @ mpHeader.stringOffset+nameOffset;

  MtDTI dtiId;
  //const MtDTI *pDti;

  nGUI_VARIABLE_init init;
  nGUI_VARIABLE_min min;
  nGUI_VARIABLE_max max;
};

struct nGUI_INPUT_CONDITION
{
  u32 nextIndex;
  //nGUI::FLOW *nextAdrs;
};

struct nGUI_FLOW_INPUT
{
  u32 conditionNum;

  u32 conditionIndex;
  nGUI_INPUT_CONDITION conditionAdrs[conditionNum] @ addressof(pInputCondition[conditionIndex]);//*
};

struct nGUI_FLOW_SWITCH
{
  u32 conditionNum;

  u32 conditionIndex;
  //nGUI_SWITCH_CONDITION *conditionAdrs;
};

struct nGUI_FLOW_FUNCTION
{
  u32 startIndex;
  //nGUI::FLOW *startAdrs;

  u32 nextIndex;
  //nGUI::FLOW *nextAdrs;

};

struct nGUI_ACTION
{
  u32 type;
  u32 objectIndex;

  u32 substitutionIndex;
  //s32 value;

  u32 propNameOffset;
  char propName[] @ mpHeader.stringOffset+propNameOffset;
};


struct nGUI_SWITCH_OPERATOR
{
  s32 value;
  u32 operatorType;
  u32 objectIndex;
};

struct nGUI_SWITCH_CONDITION
{
  u32 type;
  u32 operatorNum;

  u32 nextIndex;
  //nGUI::FLOW *nextAdrs;
  
  u32 operatorIndex;
  nGUI_SWITCH_OPERATOR operatorAdrs[operatorNum] @ addressof(pSwitchOperator[operatorIndex]);//*
};

struct nGUI_FONT
{
  u32 id;
  u32 pFont;
  //rGUIFont *pFont;
  
  u32 pathOffset;
  char path[] @ mpHeader.stringOffset+pathOffset;
};

struct nGUI_GUIRESOURCE
{
  u32 id;
  u32 pResource;
  //void *pResource;

  u32 pathOffset;
  char path[] @ mpHeader.stringOffset+pathOffset;
};

struct nGUI_GENERALRESOURCE
{
  u32 id;
  MtDTI dtiId;
  u32 pResource;
  //void *pResource;

  u32 pathOffset;
  char path[] @ mpHeader.stringOffset+pathOffset;
};

bitfield cGUIFontFilter_BITS {
  mType : 4;
  reserved: 28;
};

struct rTexture {
  MtDTI dtiId;
   
  u32 pathOffset;
  char path[] @ mpHeader.stringOffset+pathOffset; 
};

struct cGUIFontFilterGradationOverlay {
   rTexture mpTexture;//*
};

struct cGUIFontFilter : MtObject
{
  MtDTI dtiId;
  cGUIFontFilter_BITS bits;
  
  if(dtiId == MtDTI::cGUIFontFilterGradationOverlay){
    cGUIFontFilterGradationOverlay filter;
  }
};

bitfield nGUI_TEXTURE_BITS1 {
  nGUI_TEXTURE_RTYPE rtype : 2;
  resize : 1;
  reserved : 29;
};

bitfield nGUI_TEXTURE_BITS2 {
  l : 16;
  t : 16;
};

bitfield nGUI_TEXTURE_BITS3 {
  r : 16;
 b : 16;
};

struct nGUI_TEXTURE
{
  u32 id;
  nGUI_TEXTURE_BITS1 bits1;
  nGUI_TEXTURE_BITS2 bits2;
  nGUI_TEXTURE_BITS3 bits3;
  f32 clamp[4];
  f32 invSize[2];
  u32 pTexture;
  //rTexture pTexture;//*


  u32 pathOffset;
  char path[] @ mpHeader.stringOffset+pathOffset; 
    
  u32 nameOffset;
  char pName[] @ mpHeader.stringOffset+nameOffset; 
  
  u32 pad[3];
};

bitfield nGUI_OBJECT_BITS{
  initParamNum : 8;
  animateParamNum : 8;
  paddin : 16;
};

struct nGUI_OBJECT
{
  u32 id;

  nGUI_OBJECT_BITS bits;

  u32 nextIndex;
  u32 childIndex;

  u32 nameOffset;
  char pName[] @ mpHeader.stringOffset+nameOffset; 

  MtDTI dtiId;
  //  const MtDTI *pDti;
  
  u32 initParamIndex;
  //nGUI_INIT_PARAM pInitParam[initParamNum] @ ;//
      
  u32 objSequenceIndex;
  //nGUI::OBJ_SEQUENCE *pObjSequence;

  u32 extendDataOffset;
  if(extendDataOffset != 4294967295){
  //  void *pExtendData      
     u32 pExtendData @ mpHeader.extendDataOffset;
  }

};

struct rGUI_HEADER
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
    rGUI_HEADER_BITS bits;
    MtSize viewSize;

    u32 startFlowIndex;
    u32 animationOffset;
    u32 sequenceOffset;
    u32 objectOffset;
    u32 objSequenceOffset;
    u32 initParamOffset;
    u32 paramOffset;
    u32 instanceOffset;
    u32 flowOffset;
    u32 flowProcessOffset;
    u32 flowInputOffset;
    u32 flowSwitchOffset;
    u32 flowFunctionOffset;
    u32 actionOffset;
    u32 inputConditionOffset;
    u32 switchOperatorOffset;
    u32 switchConditionOffset;
    u32 variableOffset;
    u32 textureOffset;
    u32 fontOffset;
    u32 fontFilterOffset;
    u32 messageOffset;
    u32 guiResourceOffset;
    u32 generalResourceOffset;
    u32 cameraSettingOffset;
    u32 stringOffset;
    u32 keyOffset;
    u32 keyValue8Offset;
    u32 keyValue32Offset;
    u32 keyValue128Offset;
    u32 extendDataOffset;
    u32 instExeParamOffset;
    u32 vertexOffset;
};

bitfield rGUI_BITS
{
mIsSetData:
    1;
mBaseZ:
    2;
mFramerateMode:
    1;
mLanguageSettingNo:
    2;
paddin:
    26;
};

struct rGUI : cResource
{
    u32 mAttr;
    rGUI_BITS bits;
    //MtSize mViewSize;
    //char mPreviewUnitName[];
    // cGUIFontFilter mpFontFilter;//**
    // nDraw_VertexBuffer mpVertexBuffer;//*
    //rGUI_InstanceNeedObjectInfo mpInstanceNeedObjectInfo;//*
    //u32 mInstanceNullNeedNum;
    //u32 mInstanceScissorMaskNeedNum;
    //u32 mInstanceAnimationNeedNum;
    //u32 mInstanceAnimVariableNeedNum;
    //u32 mInstanceAnimControlNeedNum;
    //u32 mGUIObjTextNeedNum;
    //u32 mGUIObjMessageNeedNum;
    //u32 mGUIObjChildAnimationRootNeedNum;
    //u32 mGUIObjNullNeedNum;
    //u32 mGUIObjTextureSetNeedNum;
    //u32 mGUIObjTextureNeedNum;
    //u32 mGUIObjPolygonNeedNum;
    //u32 mGUIObjScissorMaskNeedNum;
    //u32 mGUIObjColorAdjustNeedNum;
    //u32 mGUIObjRootNeedNum;
    //u32 mGUIVarIntNeedNum;
    //u32 mGUIVarFloatNeedNum;
    //u32 mCreateAnimationBufferSize;
    //u32 mObjRootNeedSetObjectBufferSize;
};

rGUI_HEADER mpHeader @ 0x00; //*
rGUI rgui @ sizeof(mpHeader);

    // nGUI::FLOW *startFlowAdrs;
nGUI_ANIMATION pAnimation[mpHeader.animationNum] @ mpHeader.animationOffset;//*
nGUI_SEQUENCE pSequence[mpHeader.sequenceNum] @ mpHeader.sequenceOffset;//*
nGUI_OBJECT pObject[mpHeader.objectNum] @ mpHeader.objectOffset;//*
nGUI_OBJ_SEQUENCE pObjSequence[mpHeader.objSequenceNum] @ mpHeader.objSequenceOffset;//*
nGUI_INIT_PARAM pInitParam[mpHeader.initParamNum] @ mpHeader.initParamOffset;//*
nGUI_PARAM pParam[mpHeader.paramNum] @ mpHeader.paramOffset;//*
nGUI_INSTANCE pInstance[mpHeader.instanceNum] @ mpHeader.instanceOffset;//*
nGUI_FLOW pFlow[mpHeader.flowNum] @ mpHeader.flowOffset;//*
nGUI_FLOW_PROCESS pFlowProcess[mpHeader.flowProcessNum] @ mpHeader.flowProcessOffset;//*
nGUI_FLOW_INPUT pFlowInput[mpHeader.flowInputNum] @ mpHeader.flowInputOffset;//*
nGUI_FLOW_SWITCH pFlowSwitch[mpHeader.flowSwitchNum] @ mpHeader.flowSwitchOffset;//*
nGUI_FLOW_FUNCTION pFlowFunction[mpHeader.flowFunctionNum] @ mpHeader.flowFunctionOffset;//*
nGUI_ACTION pAction[mpHeader.actionNum] @ mpHeader.actionOffset;//*
nGUI_INPUT_CONDITION pInputCondition[mpHeader.inputConditionNum] @ mpHeader.inputConditionOffset;//*
nGUI_SWITCH_OPERATOR pSwitchOperator[mpHeader.switchOperatorNum] @ mpHeader.switchOperatorOffset;//*
nGUI_SWITCH_CONDITION pSwitchCondition[mpHeader.switchConditionNum] @ mpHeader.switchConditionOffset;//*
nGUI_VARIABLE pVariable[mpHeader.variableNum] @ mpHeader.variableOffset;//*
nGUI_TEXTURE pTexture[mpHeader.textureNum] @ mpHeader.textureOffset;//*
nGUI_FONT pFont[mpHeader.fontNum] @ mpHeader.fontOffset;//*
cGUIFontFilter pFontFilter[mpHeader.fontFilterNum] @ mpHeader.fontFilterOffset;//*
nGUI_MESSAGE pMessage[mpHeader.messageNum] @ mpHeader.messageOffset;//*
nGUI_GUIRESOURCE pGUIResource[mpHeader.guiResourceNum] @ mpHeader.guiResourceOffset;//*
nGUI_GENERALRESOURCE pGeneralResource[mpHeader.generalResourceNum] @ mpHeader.generalResourceOffset;//*
nGUI_CAMERA_SETTING pCameraSetting[mpHeader.cameraSettingNum] @ mpHeader.cameraSettingOffset;//*
    // MT_STR pString;
nGUI_KEY pKey[mpHeader.keyNum] @ mpHeader.keyOffset;//*
u8 pKeyValue8[mpHeader.keyNum] @ mpHeader.keyValue8Offset;//*
u8 pKeyValue32[mpHeader.keyNum] @ mpHeader.keyValue32Offset;//*
u8 pKeyValue128[mpHeader.keyNum] @ mpHeader.keyValue128Offset;//*

    // u8 *pExtendData;
//u8 pExtendData[mpHeader.instExeParamNum] @ mpHeader.extendDataOffset;//*
//nGUI_PARAM pInstExeParam[mpHeader.instExeParamNum] @ mpHeader.instExeParamOffset;//*
nGUI_VERTEX pVertex[mpHeader.vertexBufferSize/sizeof(nGUI_VERTEX)] @ mpHeader.vertexOffset;//*