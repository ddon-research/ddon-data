struct rStageCustom_Area
{
  s8 mAreaNo;
  u8 mFilterNo;
  s32 mGroupNo;
};

struct rStageCustom
{
  // rStageCustomParts mprParts;//*
  char PartsType[];
  char PartsPath[];

  u32 mArrayAreaNum;
  rStageCustom_Area mpArrayArea[mArrayAreaNum]; //*
};
rStageCustom rstagecustom_at_0x08 @0x08;