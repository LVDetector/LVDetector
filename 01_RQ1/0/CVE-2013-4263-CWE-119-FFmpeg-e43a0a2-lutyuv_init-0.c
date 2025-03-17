static av_cold int lutyuv_init(AVFilterContext *ctx)
{
    LutContext *s = ctx->priv;

    s->is_yuv = 1;

    return 0;
}
