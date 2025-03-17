authentic_sm_open(struct sc_card *card)
{
	struct sc_context *ctx = card->ctx;
	unsigned char init_data[SC_MAX_APDU_BUFFER_SIZE];
	size_t init_data_len = sizeof(init_data);
	int rv;

	LOG_FUNC_CALLED(ctx);

	memset(&card->sm_ctx.info, 0, sizeof(card->sm_ctx.info));
	memcpy(card->sm_ctx.info.config_section, card->sm_ctx.config_section, sizeof(card->sm_ctx.info.config_section));
	sc_log(ctx, "SM context config '%s'; SM mode 0x%X", card->sm_ctx.info.config_section, card->sm_ctx.sm_mode);

	if (card->sm_ctx.sm_mode == SM_MODE_TRANSMIT && card->max_send_size == 0)
		card->max_send_size = 239;

	rv = authentic_sm_acl_init (card, &card->sm_ctx.info, SM_CMD_INITIALIZE, init_data, &init_data_len);
	LOG_TEST_RET(ctx, rv, "authentIC: cannot open SM");

	rv = authentic_sm_execute (card, &card->sm_ctx.info, init_data, init_data_len, NULL, 0);
	LOG_TEST_RET(ctx, rv, "SM: execute failed");

	card->sm_ctx.info.cmd = SM_CMD_APDU_TRANSMIT;
	LOG_FUNC_RETURN(ctx, rv);
}
