GF_Err abst_dump(GF_Box *a, FILE * trace)
{
	u32 i;
	GF_AdobeBootstrapInfoBox *p = (GF_AdobeBootstrapInfoBox*)a;
	gf_isom_box_dump_start(a, "AdobeBootstrapBox", trace);

	fprintf(trace, "BootstrapinfoVersion=\"%u\" Profile=\"%u\" Live=\"%u\" Update=\"%u\" TimeScale=\"%u\" CurrentMediaTime=\""LLU"\" SmpteTimeCodeOffset=\""LLU"\" ",
	        p->bootstrapinfo_version, p->profile, p->live, p->update, p->time_scale, p->current_media_time, p->smpte_time_code_offset);
	if (p->movie_identifier)
		fprintf(trace, "MovieIdentifier=\"%s\" ", p->movie_identifier);
	if (p->drm_data)
		fprintf(trace, "DrmData=\"%s\" ", p->drm_data);
	if (p->meta_data)
		fprintf(trace, "MetaData=\"%s\" ", p->meta_data);
	fprintf(trace, ">\n");

	for (i=0; i<p->server_entry_count; i++) {
		char *str = (char*)gf_list_get(p->server_entry_table, i);
		fprintf(trace, "<ServerEntry>%s</ServerEntry>\n", str);
	}

	for (i=0; i<p->quality_entry_count; i++) {
		char *str = (char*)gf_list_get(p->quality_entry_table, i);
		fprintf(trace, "<QualityEntry>%s</QualityEntry>\n", str);
	}

	for (i=0; i<p->segment_run_table_count; i++)
		gf_isom_box_dump(gf_list_get(p->segment_run_table_entries, i), trace);

	for (i=0; i<p->fragment_run_table_count; i++)
		gf_isom_box_dump(gf_list_get(p->fragment_run_table_entries, i), trace);

	gf_isom_box_dump_done("AdobeBootstrapBox", a, trace);
	return GF_OK;
}
