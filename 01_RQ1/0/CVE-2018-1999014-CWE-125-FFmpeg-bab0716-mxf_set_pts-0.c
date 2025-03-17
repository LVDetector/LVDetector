static int mxf_set_pts(MXFContext *mxf, AVStream *st, AVPacket *pkt)
{
    AVCodecParameters *par = st->codecpar;
    MXFTrack *track = st->priv_data;

    if (par->codec_type == AVMEDIA_TYPE_VIDEO) {
        /* see if we have an index table to derive timestamps from */
        MXFIndexTable *t = mxf_find_index_table(mxf, track->index_sid);

        if (t && track->sample_count < t->nb_ptses) {
            pkt->dts = track->sample_count + t->first_dts;
            pkt->pts = t->ptses[track->sample_count];
        } else if (track->intra_only) {
            /* intra-only -> PTS = EditUnit.
             * let utils.c figure out DTS since it can be < PTS if low_delay = 0 (Sony IMX30) */
            pkt->pts = track->sample_count;
        }
        track->sample_count++;
    } else if (par->codec_type == AVMEDIA_TYPE_AUDIO) {
        int ret = mxf_set_audio_pts(mxf, par, pkt);
        if (ret < 0)
            return ret;
    } else if (track) {
        track->sample_count++;
    }
    return 0;
}
