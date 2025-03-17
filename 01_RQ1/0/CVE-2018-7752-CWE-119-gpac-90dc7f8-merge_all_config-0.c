void merge_all_config(GF_AVCConfig *avc_cfg, GF_HEVCConfig *hevc_cfg, GF_MediaBox *mdia)
{
	u32 i;
	GF_TrackReferenceTypeBox *scal = NULL;
	Track_FindRef(mdia->mediaTrack, GF_ISOM_REF_SCAL, &scal);

	if (!scal) return;

	for (i=0; i<scal->trackIDCount; i++) {
		GF_TrackBox *a_track = GetTrackbyID(mdia->mediaTrack->moov, scal->trackIDs[i]);
		GF_MPEGVisualSampleEntryBox *an_entry = NULL;
		if (a_track && a_track->Media && a_track->Media->information && a_track->Media->information->sampleTable && a_track->Media->information->sampleTable->SampleDescription)
			an_entry = (GF_MPEGVisualSampleEntryBox*)gf_list_get(a_track->Media->information->sampleTable->SampleDescription->other_boxes, 0);

		if (!an_entry) continue;

		if (avc_cfg && an_entry->svc_config && an_entry->svc_config->config)
			merge_avc_config(avc_cfg, an_entry->svc_config->config);

		if (avc_cfg && an_entry->mvc_config && an_entry->mvc_config->config)
			merge_avc_config(avc_cfg, an_entry->mvc_config->config);

		if (avc_cfg && an_entry->avc_config && an_entry->avc_config->config)
			merge_avc_config(avc_cfg, an_entry->avc_config->config);

		if (hevc_cfg && an_entry->lhvc_config && an_entry->lhvc_config->config)
			merge_hevc_config(hevc_cfg, an_entry->lhvc_config->config, GF_TRUE);

		if (hevc_cfg && an_entry->hevc_config && an_entry->hevc_config->config)
			merge_hevc_config(hevc_cfg, an_entry->hevc_config->config, GF_TRUE);
	}

	if (hevc_cfg) hevc_cfg->is_lhvc = GF_FALSE;
}
