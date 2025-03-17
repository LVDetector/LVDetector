ipxsap_string(netdissect_options *ndo, u_short port)
{
	register char *cp;
	register struct hnamemem *tp;
	register uint32_t i = port;
	char buf[sizeof("0000")];

	for (tp = &ipxsaptable[i & (HASHNAMESIZE-1)]; tp->nxt; tp = tp->nxt)
		if (tp->addr == i)
			return (tp->name);

	tp->addr = i;
	tp->nxt = newhnamemem(ndo);

	cp = buf;
	NTOHS(port);
	*cp++ = hex[port >> 12 & 0xf];
	*cp++ = hex[port >> 8 & 0xf];
	*cp++ = hex[port >> 4 & 0xf];
	*cp++ = hex[port & 0xf];
	*cp++ = '\0';
	tp->name = strdup(buf);
	if (tp->name == NULL)
		(*ndo->ndo_error)(ndo, "ipxsap_string: strdup(buf)");
	return (tp->name);
}
