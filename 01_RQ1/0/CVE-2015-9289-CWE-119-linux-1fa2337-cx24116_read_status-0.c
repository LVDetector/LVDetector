static int cx24116_read_status(struct dvb_frontend *fe, fe_status_t *status)
{
	struct cx24116_state *state = fe->demodulator_priv;

	int lock = cx24116_readreg(state, CX24116_REG_SSTATUS) &
		CX24116_STATUS_MASK;

	dprintk("%s: status = 0x%02x\n", __func__, lock);

	*status = 0;

	if (lock & CX24116_HAS_SIGNAL)
		*status |= FE_HAS_SIGNAL;
	if (lock & CX24116_HAS_CARRIER)
		*status |= FE_HAS_CARRIER;
	if (lock & CX24116_HAS_VITERBI)
		*status |= FE_HAS_VITERBI;
	if (lock & CX24116_HAS_SYNCLOCK)
		*status |= FE_HAS_SYNC | FE_HAS_LOCK;

	return 0;
}
