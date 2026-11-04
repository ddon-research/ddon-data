#!/bin/bash

season1Ext=(2EA55F30 3FD51519 46ECE09C 4BB8A7C5 5362A636 5810D1F1 60BA5E0B 767645BE aad abd abl ach acv ajp ala ali alp amr ams amsd aps arc ari arj ars aser atk bap bft bjt btb caip ccp cda cdarate cdl cdl_pawn cdrr cdrt cecp cee chant cip ckb ckc ckg cks ckst col cpe cpl cqa cqi cql cqr cqw crs csd csl ctc cuex dgm dja dja_pawn dme dmt dtt dvw dwm e2d ean ebi_sv ect edt edt_color_def edt_mod_pal edt_muscle edt_pset_pal edt_tex_pal edt_voice_pal edv eef efl efs ele eli em_scr_adj ema emg eoc epi epp epv equip_preset equr era esa esh esl esn esp est evl evp ewk exp f2p fat_adjust fbik_human2 fedt_jntpreset fmd fsm gat gfd gii gmd gmp gpl grs grw gui head_ctrl hmcs hmeparam hmeq hmpre ik ikctrl ipa ir_adj jex2 jlt2 jmc jmp jnt_info jnt_order jobbase jtq kcp lcd lcm lcp ldp leg_ctrl lmt lop lot lrc lup mcw mgcc mod mot_filter motparam mrl mser mss nav nci ncs ndp ned nll nmp nms nsd oIp occ oce olp omp opp osp paa pam pao pas paw pen pep phs plt prs psi ptc ptk push_rate qhd qmi qsq qst qtd rag rbd rcp repgmdlist revr rsl rtex sal sar sbb sbc sbkr sbv sca sce sck scp scsr sdl sdsr sdt sg_tbl shake_ctrl shi shl sja sky slm slt smc smp sms smxr sn2 sot spg_tbl spl spo sri srqr ssqr sta stc sti stp stqr sts swm tcm tco tde tdm tex tlt tmc tmo tqg txt vib wal wcrt wep wpn_ofs wpt wrt wsi wta wte wtf wtl xsew zon)

for ext in ${season1Ext[@]}; do
	echo "${ext}," >>season1headers.csv
	find /d/DDON_01010004/nativePC/rom -type f -name "*.${ext}" -print -exec xxd -l 4 {} \; -quit | tee -a season1headers.csv
	echo -e "\n" >>season1headers.csv
done
