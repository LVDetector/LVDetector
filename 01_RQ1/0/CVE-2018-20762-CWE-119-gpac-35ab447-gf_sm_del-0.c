void gf_sm_del(GF_SceneManager *ctx)
{
	u32 count;
	while ( (count = gf_list_count(ctx->streams)) ) {
		GF_StreamContext *sc = (GF_StreamContext *)gf_list_get(ctx->streams, count-1);
		gf_list_rem(ctx->streams, count-1);
		gf_sm_delete_stream(sc);
	}
	gf_list_del(ctx->streams);
	if (ctx->root_od) gf_odf_desc_del((GF_Descriptor *) ctx->root_od);
	gf_free(ctx);
}
