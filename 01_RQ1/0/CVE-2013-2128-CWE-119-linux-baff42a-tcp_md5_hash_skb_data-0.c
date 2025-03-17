int tcp_md5_hash_skb_data(struct tcp_md5sig_pool *hp,
			  struct sk_buff *skb, unsigned header_len)
{
	struct scatterlist sg;
	const struct tcphdr *tp = tcp_hdr(skb);
	struct hash_desc *desc = &hp->md5_desc;
	unsigned i;
	const unsigned head_data_len = skb_headlen(skb) > header_len ?
				       skb_headlen(skb) - header_len : 0;
	const struct skb_shared_info *shi = skb_shinfo(skb);

	sg_init_table(&sg, 1);

	sg_set_buf(&sg, ((u8 *) tp) + header_len, head_data_len);
	if (crypto_hash_update(desc, &sg, head_data_len))
		return 1;

	for (i = 0; i < shi->nr_frags; ++i) {
		const struct skb_frag_struct *f = &shi->frags[i];
		sg_set_page(&sg, f->page, f->size, f->page_offset);
		if (crypto_hash_update(desc, &sg, f->size))
			return 1;
	}

	return 0;
}
