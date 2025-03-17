cdf_dump_stream(const cdf_header_t *h, const cdf_stream_t *sst)
{
	size_t ss = sst->sst_dirlen < h->h_min_size_standard_stream ?
	    CDF_SHORT_SEC_SIZE(h) : CDF_SEC_SIZE(h);
	cdf_dump(sst->sst_tab, ss * sst->sst_len);
}
