GF_Err lsr1_Write(GF_Box *s, GF_BitStream *bs)
{
	GF_Err e;
	GF_LASeRSampleEntryBox *ptr = (GF_LASeRSampleEntryBox *)s;
	e = gf_isom_box_write_header(s, bs);
	if (e) return e;

	gf_bs_write_data(bs, ptr->reserved, 6);
	gf_bs_write_u16(bs, ptr->dataReferenceIndex);
	if (ptr->lsr_config) {
		e = gf_isom_box_write((GF_Box *)ptr->lsr_config, bs);
		if (e) return e;
	}
	if (ptr->descr) {
		e = gf_isom_box_write((GF_Box *)ptr->descr, bs);
		if (e) return e;
	}
	return e;
}
