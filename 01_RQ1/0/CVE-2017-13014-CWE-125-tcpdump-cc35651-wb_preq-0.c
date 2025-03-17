wb_preq(netdissect_options *ndo,
        const struct pkt_preq *preq, u_int len)
{
	ND_PRINT((ndo, " wb-preq:"));
	if (len < sizeof(*preq) || !ND_TTEST(*preq))
		return (-1);

	ND_PRINT((ndo, " need %u/%s:%u",
	       EXTRACT_32BITS(&preq->pp_low),
	       ipaddr_string(ndo, &preq->pp_page.p_sid),
	       EXTRACT_32BITS(&preq->pp_page.p_uid)));
	return (0);
}
