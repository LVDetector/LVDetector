do_os_note(struct magic_set *ms, unsigned char *nbuf, uint32_t type,
    int swap, uint32_t namesz, uint32_t descsz,
    size_t noff, size_t doff, int *flags)
{
	if (namesz == 5 && strcmp((char *)&nbuf[noff], "SuSE") == 0 &&
		type == NT_GNU_VERSION && descsz == 2) {
		*flags |= FLAGS_DID_OS_NOTE;
		if (file_printf(ms, ", for SuSE %d.%d", nbuf[doff],
		    nbuf[doff + 1]) == -1)
		    return -1;
	    return 1;
	}

	if (namesz == 4 && strcmp((char *)&nbuf[noff], "GNU") == 0 &&
	    type == NT_GNU_VERSION && descsz == 16) {
		uint32_t desc[4];
		memcpy(desc, &nbuf[doff], sizeof(desc));

		*flags |= FLAGS_DID_OS_NOTE;
		if (file_printf(ms, ", for GNU/") == -1)
			return 1;
		switch (elf_getu32(swap, desc[0])) {
		case GNU_OS_LINUX:
			if (file_printf(ms, "Linux") == -1)
				return 1;
			break;
		case GNU_OS_HURD:
			if (file_printf(ms, "Hurd") == -1)
				return 1;
			break;
		case GNU_OS_SOLARIS:
			if (file_printf(ms, "Solaris") == -1)
				return 1;
			break;
		case GNU_OS_KFREEBSD:
			if (file_printf(ms, "kFreeBSD") == -1)
				return 1;
			break;
		case GNU_OS_KNETBSD:
			if (file_printf(ms, "kNetBSD") == -1)
				return 1;
			break;
		default:
			if (file_printf(ms, "<unknown>") == -1)
				return 1;
		}
		if (file_printf(ms, " %d.%d.%d", elf_getu32(swap, desc[1]),
		    elf_getu32(swap, desc[2]), elf_getu32(swap, desc[3])) == -1)
			return 1;
		return 1;
	}

	if (namesz == 7 && strcmp((char *)&nbuf[noff], "NetBSD") == 0) {
	    	if (type == NT_NETBSD_VERSION && descsz == 4) {
			*flags |= FLAGS_DID_OS_NOTE;
			do_note_netbsd_version(ms, swap, &nbuf[doff]);
			return 1;
		}
	}

	if (namesz == 8 && strcmp((char *)&nbuf[noff], "FreeBSD") == 0) {
	    	if (type == NT_FREEBSD_VERSION && descsz == 4) {
			*flags |= FLAGS_DID_OS_NOTE;
			do_note_freebsd_version(ms, swap, &nbuf[doff]);
			return 1;
		}
	}

	if (namesz == 8 && strcmp((char *)&nbuf[noff], "OpenBSD") == 0 &&
	    type == NT_OPENBSD_VERSION && descsz == 4) {
		*flags |= FLAGS_DID_OS_NOTE;
		if (file_printf(ms, ", for OpenBSD") == -1)
			return 1;
		/* Content of note is always 0 */
		return 1;
	}

	if (namesz == 10 && strcmp((char *)&nbuf[noff], "DragonFly") == 0 &&
	    type == NT_DRAGONFLY_VERSION && descsz == 4) {
		uint32_t desc;
		*flags |= FLAGS_DID_OS_NOTE;
		if (file_printf(ms, ", for DragonFly") == -1)
			return 1;
		memcpy(&desc, &nbuf[doff], sizeof(desc));
		desc = elf_getu32(swap, desc);
		if (file_printf(ms, " %d.%d.%d", desc / 100000,
		    desc / 10000 % 10, desc % 10000) == -1)
			return 1;
		return 1;
	}
	return 0;
}
