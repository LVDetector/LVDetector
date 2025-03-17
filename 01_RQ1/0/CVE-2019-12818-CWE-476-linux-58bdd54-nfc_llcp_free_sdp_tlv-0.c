void nfc_llcp_free_sdp_tlv(struct nfc_llcp_sdp_tlv *sdp)
{
	kfree(sdp->tlv);
	kfree(sdp);
}
