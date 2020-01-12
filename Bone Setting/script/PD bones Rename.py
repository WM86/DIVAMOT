# License: Don't worry, it's a free gift to the world. 
# This Blender python script is for the purpose of mass renaming bones from a DAZ/Poser armature to MikuMikDance Japanese bone names. The armature animation with renamed bones can then be exported as a VMD animation using the mmd_tools Blender add-on (powroupi fork). Run this script from the Blender text editor. The armature object of the imported CMU BVH animation must be the active object.


CMU_bvh_bones_dict = {0: 'n_hara_cp', 1: 'kl_kosi_etc_wj', 2: 'j_mune_wj', 3: 'kl_mune_b_wj', 4: 'kl_kubi', 5: 'unuse', 
6: 'kl_eye_l', 7: 'kl_eye_r', 8: 'kl_waki_l_wj', 9: 'n_ste_l_wj_ex', 10: 'n_skata_b_l_wj_cd_cu_ex', 
11: 'kl_waki_r_wj', 12: 'n_ste_r_wj_ex', 13: 'n_skata_b_r_wj_cd_cu_ex', 14: 'cl_momo_l', 15: 'kl_asi_l_wj_co', 
16: 'cl_momo_r', 17: 'kl_asi_r_wj_co', 18: 'j_ude_l_wj', 19: 'j_ude_r_wj', 20: 'n_sude_b_l_wj_ex', 
21: 'n_sude_b_r_wj_ex', 22: 'e_sune_l_cp', 23: 'e_sune_r_cp', 24: 'nl_hito_r_wj', 25: 'nl_hito_b_r_wj', 
26: 'nl_hito_c_r_wj', 27: 'nl_ko_r_wj', 28: 'nl_ko_b_r_wj', 29: 'nl_ko_c_r_wj', 30: 'nl_kusu_r_wj', 
31: 'nl_kusu_b_r_wj', 32: 'nl_kusu_c_r_wj', 33: 'nl_naka_r_wj', 34: 'nl_naka_b_r_wj', 35: 'nl_naka_c_r_wj', 
36: 'nl_oya_r_wj', 37: 'nl_oya_b_r_wj', 38: 'nl_oya_c_r_wj', 39: 'nl_hito_l_wj', 40: 'nl_hito_b_l_wj', 
41: 'nl_hito_c_l_wj', 42: 'nl_ko_l_wj', 43: 'nl_ko_b_l_wj', 44: 'nl_ko_c_l_wj', 45: 'nl_kusu_l_wj', 
46: 'nl_kusu_b_l_wj', 47: 'nl_kusu_c_l_wj', 48: 'nl_naka_l_wj', 49: 'nl_naka_b_l_wj', 50: 'nl_naka_c_l_wj', 
51: 'nl_oya_l_wj', 52: 'nl_oya_b_l_wj', 53: 'nl_oya_c_l_wj', 54:'gblctr', 55: 'kl_hara_etc', 
56: 'j_kao_wj', 57: 'n_skata_l_wj_cd_ex', 58: 'n_skata_r_wj_cd_ex', 59: 'kg_hara_y', 60:'kl_toe_l_wj', 
61:'kl_toe_r_wj'}

CMU_bvh_MMD_bones_Japanese = {0: 'センター', 1: '下半身', 2: '上半身', 3: '上半身2', 4: '首', 5: 'unuse', 
6: '左目', 7: '右目', 8: '左肩', 9: '左手首', 10: '左腕捩', 
11: '右肩', 12: '右手首', 13: '右腕捩', 14: '左足', 15: '左足首', 
16: '右足', 17: '右足首', 18: '左ひじ', 19: '右ひじ', 20: '左手捩', 
21: '右手捩', 22: '左足ＩＫ', 23: '右足ＩＫ', 24: '右人指１', 25: '右人指２', 
26: '右人指３', 27: '右小指１', 28: '右小指２', 29: '右小指３', 30: '右薬指１', 
31: '右薬指２', 32: '右薬指３', 33: '右中指１', 34: '右中指２', 35: '右中指３', 
36: '右親指０', 37: '右親指１', 38: '右親指２', 39: '左人指１', 40: '左人指２', 
41: '左人指３', 42: '左小指１', 43: '左小指２', 44: '左小指３', 45: '左薬指１', 
46: '左薬指２', 47: '左薬指３', 48: '左中指１', 49: '左中指２', 50: '左中指３', 
51: '左親指０', 52: '左親指１', 53: '左親指２', 54: '全ての親', 55: '腰', 
56: '頭', 57: '左腕', 58: '右腕', 59: 'グルーブ', 60:'左足先EX', 61:'右足先EX'}

original_bone_names = CMU_bvh_bones_dict
renamed_bones_names = CMU_bvh_MMD_bones_Japanese

import bpy

#use international fonts and display the names of the bones
def use_international_fonts_display_names_bones():
	bpy.context.user_preferences.system.use_international_fonts = True
	bpy.context.object.data.show_names = True


#rename all bones from CMU DAZ bone names to MMD Japanese bone names
def rename_bones():
	bpy.ops.object.mode_set(mode='OBJECT')
	for i in original_bone_names.keys():
		if original_bone_names[i] in bpy.context.active_object.data.bones.keys():
			bpy.context.active_object.data.bones[original_bone_names[i]].name = renamed_bones_names[i]

use_international_fonts_display_names_bones()
rename_bones()
bpy.ops.object.mode_set(mode='POSE')
bpy.ops.pose.select_all(action='SELECT')

