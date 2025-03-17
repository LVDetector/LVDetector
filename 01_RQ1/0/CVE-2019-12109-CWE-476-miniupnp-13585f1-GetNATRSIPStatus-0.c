GetNATRSIPStatus(struct upnphttp * h, const char * action, const char * ns)
{
#if 0
	static const char resp[] =
		"<u:GetNATRSIPStatusResponse "
		"xmlns:u=\"" SERVICE_TYPE_WANIPC "\">"
		"<NewRSIPAvailable>0</NewRSIPAvailable>"
		"<NewNATEnabled>1</NewNATEnabled>"
		"</u:GetNATRSIPStatusResponse>";
	UNUSED(action);
#endif
	static const char resp[] =
		"<u:%sResponse "
		"xmlns:u=\"%s\">"
		"<NewRSIPAvailable>0</NewRSIPAvailable>"
		"<NewNATEnabled>1</NewNATEnabled>"
		"</u:%sResponse>";
	char body[512];
	int bodylen;
	/* 2.2.9. RSIPAvailable
	 * This variable indicates if Realm-specific IP (RSIP) is available
	 * as a feature on the InternetGatewayDevice. RSIP is being defined
	 * in the NAT working group in the IETF to allow host-NATing using
	 * a standard set of message exchanges. It also allows end-to-end
	 * applications that otherwise break if NAT is introduced
	 * (e.g. IPsec-based VPNs).
	 * A gateway that does not support RSIP should set this variable to 0. */
	bodylen = snprintf(body, sizeof(body), resp,
		action, ns, /*SERVICE_TYPE_WANIPC,*/
		action);
	BuildSendAndCloseSoapResp(h, body, bodylen);
}
