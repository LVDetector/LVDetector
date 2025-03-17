GF_Err audio_sample_entry_Write(GF_Box *s, GF_BitStream *bs)
{
	GF_Err e;
	GF_MPEGAudioSampleEntryBox *ptr = (GF_MPEGAudioSampleEntryBox *)s;
	e = gf_isom_box_write_header(s, bs);
	if (e) return e;
	gf_isom_audio_sample_entry_write((GF_AudioSampleEntryBox*)s, bs);
	if (ptr->esd) {
		e = gf_isom_box_write((GF_Box *)ptr->esd, bs);
		if (e) return e;
	}
	if (ptr->cfg_3gpp) {
		e = gf_isom_box_write((GF_Box *)ptr->cfg_3gpp, bs);
		if (e) return e;
	}
	if (ptr->cfg_ac3) {
		e = gf_isom_box_write((GF_Box *)ptr->cfg_ac3, bs);
		if (e) return e;
	}
	return gf_isom_box_array_write(s, ptr->protections, bs);
}
