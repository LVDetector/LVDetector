static IHEVCD_ERROR_T ihevcd_profile_tier_level(bitstrm_t *ps_bitstrm,
 profile_tier_lvl_info_t *ps_ptl,
                                                WORD32 profile_present,
                                                WORD32 max_num_sub_layers)
{
    WORD32 value;
    IHEVCD_ERROR_T ret = (IHEVCD_ERROR_T)IHEVCD_SUCCESS;
    WORD32 i;

 if(profile_present)
 {
        ret = ihevcd_parse_profile_tier_level_layer(ps_bitstrm, &ps_ptl->s_ptl_gen);
 }

    BITS_PARSE("general_level_idc", value, ps_bitstrm, 8);
    ps_ptl->s_ptl_gen.u1_level_idc = value;


 for(i = 0; i < max_num_sub_layers; i++)
 {
        BITS_PARSE("sub_layer_profile_present_flag[i]", value, ps_bitstrm, 1);
        ps_ptl->ai1_sub_layer_profile_present_flag[i] = value;

        BITS_PARSE("sub_layer_level_present_flag[i]", value, ps_bitstrm, 1);
        ps_ptl->ai1_sub_layer_level_present_flag[i] = value;
 }

 if(max_num_sub_layers > 0)
 {
 for(i = max_num_sub_layers; i < 8; i++)
 {
            BITS_PARSE("reserved_zero_2bits", value, ps_bitstrm, 2);
 }
 }

 for(i = 0; i < max_num_sub_layers; i++)
 {
 if(ps_ptl->ai1_sub_layer_profile_present_flag[i])
 {
            ret = ihevcd_parse_profile_tier_level_layer(ps_bitstrm,
 &ps_ptl->as_ptl_sub[i]);
 }
 if(ps_ptl->ai1_sub_layer_level_present_flag[i])
 {
            BITS_PARSE("sub_layer_level_idc[i]", value, ps_bitstrm, 8);
            ps_ptl->as_ptl_sub[i].u1_level_idc = value;

 }
 }



 return ret;
}
