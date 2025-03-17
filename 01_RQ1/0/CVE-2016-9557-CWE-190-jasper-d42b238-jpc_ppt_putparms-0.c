static int jpc_ppt_putparms(jpc_ms_t *ms, jpc_cstate_t *cstate, jas_stream_t *out)
{
	jpc_ppt_t *ppt = &ms->parms.ppt;

	/* Eliminate compiler warning about unused variable. */
	cstate = 0;

	if (jpc_putuint8(out, ppt->ind)) {
		return -1;
	}
	if (jas_stream_write(out, (char *) ppt->data, ppt->len) != JAS_CAST(int, ppt->len)) {
		return -1;
	}
	return 0;
}
