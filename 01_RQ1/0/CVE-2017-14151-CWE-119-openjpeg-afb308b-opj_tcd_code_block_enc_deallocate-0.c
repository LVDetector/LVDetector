static void opj_tcd_code_block_enc_deallocate(opj_tcd_precinct_t * p_precinct)
{
    OPJ_UINT32 cblkno, l_nb_code_blocks;

    opj_tcd_cblk_enc_t * l_code_block = p_precinct->cblks.enc;
    if (l_code_block) {
        l_nb_code_blocks = p_precinct->block_size / sizeof(opj_tcd_cblk_enc_t);

        for (cblkno = 0; cblkno < l_nb_code_blocks; ++cblkno)  {
            if (l_code_block->data) {
                /* We refer to data - 1 since below we incremented it */
                /* in opj_tcd_code_block_enc_allocate_data() */
                opj_free(l_code_block->data - 1);
                l_code_block->data = 00;
            }

            if (l_code_block->layers) {
                opj_free(l_code_block->layers);
                l_code_block->layers = 00;
            }

            if (l_code_block->passes) {
                opj_free(l_code_block->passes);
                l_code_block->passes = 00;
            }
            ++l_code_block;
        }

        opj_free(p_precinct->cblks.enc);

        p_precinct->cblks.enc = 00;
    }
}
