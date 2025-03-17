av_cold void ff_mpeg4videodec_static_init(void) {
    static int done = 0;

    if (!done) {
        ff_rl_init(&ff_mpeg4_rl_intra, ff_mpeg4_static_rl_table_store[0]);
        ff_rl_init(&ff_rvlc_rl_inter, ff_mpeg4_static_rl_table_store[1]);
        ff_rl_init(&ff_rvlc_rl_intra, ff_mpeg4_static_rl_table_store[2]);
        INIT_VLC_RL(ff_mpeg4_rl_intra, 554);
        INIT_VLC_RL(ff_rvlc_rl_inter, 1072);
        INIT_VLC_RL(ff_rvlc_rl_intra, 1072);
        INIT_VLC_STATIC(&dc_lum, DC_VLC_BITS, 10 /* 13 */,
                        &ff_mpeg4_DCtab_lum[0][1], 2, 1,
                        &ff_mpeg4_DCtab_lum[0][0], 2, 1, 512);
        INIT_VLC_STATIC(&dc_chrom, DC_VLC_BITS, 10 /* 13 */,
                        &ff_mpeg4_DCtab_chrom[0][1], 2, 1,
                        &ff_mpeg4_DCtab_chrom[0][0], 2, 1, 512);
        INIT_VLC_STATIC(&sprite_trajectory, SPRITE_TRAJ_VLC_BITS, 15,
                        &ff_sprite_trajectory_tab[0][1], 4, 2,
                        &ff_sprite_trajectory_tab[0][0], 4, 2, 128);
        INIT_VLC_STATIC(&mb_type_b_vlc, MB_TYPE_B_VLC_BITS, 4,
                        &ff_mb_type_b_tab[0][1], 2, 1,
                        &ff_mb_type_b_tab[0][0], 2, 1, 16);
        done = 1;
    }
}
