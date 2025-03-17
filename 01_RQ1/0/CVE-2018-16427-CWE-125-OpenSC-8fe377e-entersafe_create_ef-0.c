static int entersafe_create_ef(sc_card_t *card, sc_entersafe_create_data * data)
{
	int r;
	sc_apdu_t apdu;

	SC_FUNC_CALLED(card->ctx, SC_LOG_DEBUG_VERBOSE);

	sc_format_apdu(card, &apdu, SC_APDU_CASE_3_SHORT, 0xE0, 0x02, 0x00);
	apdu.cla = 0x84;
	apdu.data = (u8*)&data->data.ef;
	apdu.lc = apdu.datalen = sizeof(data->data.ef);

	r = entersafe_transmit_apdu(card, &apdu,init_key,sizeof(init_key),0,1);
	SC_TEST_RET(card->ctx, SC_LOG_DEBUG_NORMAL, r, "APDU transmit failed");
	return sc_check_sw(card, apdu.sw1, apdu.sw2);
}
