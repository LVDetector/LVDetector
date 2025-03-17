void vp7_decode_mvs(VP8Context *s, VP8Macroblock *mb,
                    int mb_x, int mb_y, int layout)
{
    VP8Macroblock *mb_edge[12];
    enum { CNT_ZERO, CNT_NEAREST, CNT_NEAR };
    enum { VP8_EDGE_TOP, VP8_EDGE_LEFT, VP8_EDGE_TOPLEFT };
    int idx = CNT_ZERO;
    VP56mv near_mv[3];
    uint8_t cnt[3] = { 0 };
    VP56RangeCoder *c = &s->c;
    int i;

    AV_ZERO32(&near_mv[0]);
    AV_ZERO32(&near_mv[1]);
    AV_ZERO32(&near_mv[2]);

    for (i = 0; i < VP7_MV_PRED_COUNT; i++) {
        const VP7MVPred * pred = &vp7_mv_pred[i];
        int edge_x, edge_y;

        if (vp7_calculate_mb_offset(mb_x, mb_y, s->mb_width, pred->xoffset,
                                    pred->yoffset, !s->profile, &edge_x, &edge_y)) {
            VP8Macroblock *edge = mb_edge[i] = (s->mb_layout == 1)
                                             ? s->macroblocks_base + 1 + edge_x +
                                               (s->mb_width + 1) * (edge_y + 1)
                                             : s->macroblocks + edge_x +
                                               (s->mb_height - edge_y - 1) * 2;
            uint32_t mv = AV_RN32A(get_bmv_ptr(edge, vp7_mv_pred[i].subblock));
            if (mv) {
                if (AV_RN32A(&near_mv[CNT_NEAREST])) {
                    if (mv == AV_RN32A(&near_mv[CNT_NEAREST])) {
                        idx = CNT_NEAREST;
                    } else if (AV_RN32A(&near_mv[CNT_NEAR])) {
                        if (mv != AV_RN32A(&near_mv[CNT_NEAR]))
                            continue;
                        idx = CNT_NEAR;
                    } else {
                        AV_WN32A(&near_mv[CNT_NEAR], mv);
                        idx = CNT_NEAR;
                    }
                } else {
                    AV_WN32A(&near_mv[CNT_NEAREST], mv);
                    idx = CNT_NEAREST;
                }
            } else {
                idx = CNT_ZERO;
            }
        } else {
            idx = CNT_ZERO;
        }
        cnt[idx] += vp7_mv_pred[i].score;
    }

    mb->partitioning = VP8_SPLITMVMODE_NONE;

    if (vp56_rac_get_prob_branchy(c, vp7_mode_contexts[cnt[CNT_ZERO]][0])) {
        mb->mode = VP8_MVMODE_MV;

        if (vp56_rac_get_prob_branchy(c, vp7_mode_contexts[cnt[CNT_NEAREST]][1])) {

            if (vp56_rac_get_prob_branchy(c, vp7_mode_contexts[cnt[CNT_NEAR]][2])) {

                if (cnt[CNT_NEAREST] > cnt[CNT_NEAR])
                    AV_WN32A(&mb->mv, cnt[CNT_ZERO] > cnt[CNT_NEAREST] ? 0 : AV_RN32A(&near_mv[CNT_NEAREST]));
                else
                    AV_WN32A(&mb->mv, cnt[CNT_ZERO] > cnt[CNT_NEAR]    ? 0 : AV_RN32A(&near_mv[CNT_NEAR]));

                if (vp56_rac_get_prob_branchy(c, vp7_mode_contexts[cnt[CNT_NEAR]][3])) {
                    mb->mode = VP8_MVMODE_SPLIT;
                    mb->mv = mb->bmv[decode_splitmvs(s, c, mb, layout, IS_VP7) - 1];
                } else {
                    mb->mv.y += vp7_read_mv_component(c, s->prob->mvc[0]);
                    mb->mv.x += vp7_read_mv_component(c, s->prob->mvc[1]);
                    mb->bmv[0] = mb->mv;
                }
            } else {
                mb->mv = near_mv[CNT_NEAR];
                mb->bmv[0] = mb->mv;
            }
        } else {
            mb->mv = near_mv[CNT_NEAREST];
            mb->bmv[0] = mb->mv;
        }
    } else {
        mb->mode = VP8_MVMODE_ZERO;
        AV_ZERO32(&mb->mv);
        mb->bmv[0] = mb->mv;
    }
}
