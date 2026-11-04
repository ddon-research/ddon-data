#!/bin/bash

season2Ext=(aad abd abl ach acv ajp ala ali alp aml amr ams amsd aps arc ari arj ars aser atk bap bft bjt blow_save btb caip ccp cda cdarate cdl cdl_pawn cdrr cdrt cecp cee chant cip ckc cks col cpe cpl cqi cql cqr crs csd csl ctc cuex damage_save damage_spAdj dgm dja dja_pawn dme dmi dmt dtt dvw dwm e2d ean ebi_sv ebs ect edt edt_color_def edt_mod_pal edt_muscle edt_pset_pal edt_tex_pal edt_voice_pal edv eef efl efs ele eli em_scr_adj ema emg eoc epi epp epv equip_preset equr era eroSmall_info eroSuper_info ero_addTime esa esh esl esn esp est evl evp ewk ewp 2EA55F30 exp f2p faa fal fat_adjust fbik_human2 fedt_jntpreset fmd fmi fnd fng fni fnl fsm gat gfd gii gmd gmp gpl grs grw gui head_ctrl hmcs hmeparam hmeq hmpre ik ikctrl ipa ir_adj ir_adj_pl jex2 jlt2 jmc jmp jnt_info jnt_order jobbase jtq kcp kctt lae lai lcd lcm lcp ldp leg_ctrl lmt lop lot lrc lup mcw mgcc mod mot_filter motparam mra mrl msd mser msl mss nav nci ncs ndp ned nem nll nmm nmp nms nsd nsp oIp occ oce olp omk omp opp osp paa pam pao pas paw peg pen pep phs plt ppr ppt pqt prs psi ptc ptc ptk push_rate qhd qmi qsq qst qtd rac rag rbd reg_ersion reg_info repgmdlist revr rsl rtex rwr sal sar sbb sbc sbkr sbv sca scc sce sck scl_change scp scpx scsr sdl sdsr sdt sg_tbl shake_ctrl shi shl sja sky slm slt smc smp sms smxr sn2 sot spg_tbl spl spo sri sri2 srqr ssqr sta stc sti stp stqr sts swm tags tcm tco tde tdm tex tlt tmc tmo tqg txt ujp vib wal wallmaria wcrt wep wp2 wpn_ofs wpt wrt wsi wta wte wtf wtl xsew zon)

for ext in ${season2Ext[@]}; do
	echo "${ext}," >>season2headers.csv
	find /d/DDON_02030004/nativePC/rom -type f -name "*.${ext}" -print -exec xxd -l 4 {} \; -quit | tee -a season2headers.csv
	echo -e "\n" >>season2headers.csv
done
