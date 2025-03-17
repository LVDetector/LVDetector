static int process_split_xxclude(struct openconnect_info *vpninfo,
				 int include, const char *route, int *v4_incs,
				 int *v6_incs)
{
	struct in_addr addr;
	const char *in_ex = include?"IN":"EX";
	char envname[80];
	char *slash;

	slash = strchr(route, '/');
	if (!slash) {
	badinc:
		if (include)
			vpn_progress(vpninfo, PRG_ERR,
				     _("Discard bad split include: \"%s\"\n"),
				     route);
		else
			vpn_progress(vpninfo, PRG_ERR,
				     _("Discard bad split exclude: \"%s\"\n"),
				     route);
		return -EINVAL;
	}

	*slash = 0;

	if (strchr(route, ':')) {
		snprintf(envname, 79, "CISCO_IPV6_SPLIT_%sC_%d_ADDR", in_ex,
			 *v6_incs);
		setenv(envname, route, 1);

		snprintf(envname, 79, "CISCO_IPV6_SPLIT_%sC_%d_MASKLEN", in_ex,
			 *v6_incs);
		setenv(envname, slash+1, 1);

		(*v6_incs)++;
		return 0;
	}
		
	if (!inet_aton(route, &addr)) {
		*slash = '/';
		goto badinc;
	}

	envname[79] = 0;
	snprintf(envname, 79, "CISCO_SPLIT_%sC_%d_ADDR", in_ex, *v4_incs);
	setenv(envname, route, 1);

	/* Put it back how we found it */
	*slash = '/';

	if (!inet_aton(slash+1, &addr))
		goto badinc;

	snprintf(envname, 79, "CISCO_SPLIT_%sC_%d_MASK", in_ex, *v4_incs);
	setenv(envname, slash+1, 1);

	snprintf(envname, 79, "CISCO_SPLIT_%sC_%d_MASKLEN", in_ex, *v4_incs);
	setenv_int(envname, netmasklen(addr));

	(*v4_incs)++;
	return 0;
}
