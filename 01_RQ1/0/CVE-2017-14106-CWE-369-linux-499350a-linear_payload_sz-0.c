static int linear_payload_sz(bool first_skb)
{
	if (first_skb)
		return SKB_WITH_OVERHEAD(2048 - MAX_TCP_HEADER);
	return 0;
}
