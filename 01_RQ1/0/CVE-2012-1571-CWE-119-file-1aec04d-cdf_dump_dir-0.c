cdf_dump_dir(const cdf_info_t *info, const cdf_header_t *h,
    const cdf_sat_t *sat, const cdf_sat_t *ssat, const cdf_stream_t *sst,
    const cdf_dir_t *dir)
{
	size_t i, j;
	cdf_directory_t *d;
	char name[__arraycount(d->d_name)];
	cdf_stream_t scn;
	struct timespec ts;

	static const char *types[] = { "empty", "user storage",
	    "user stream", "lockbytes", "property", "root storage" };

	for (i = 0; i < dir->dir_len; i++) {
		d = &dir->dir_tab[i];
		for (j = 0; j < sizeof(name); j++)
			name[j] = (char)CDF_TOLE2(d->d_name[j]);
		(void)fprintf(stderr, "Directory %" SIZE_T_FORMAT "u: %s\n",
		    i, name);
		if (d->d_type < __arraycount(types))
			(void)fprintf(stderr, "Type: %s\n", types[d->d_type]);
		else
			(void)fprintf(stderr, "Type: %d\n", d->d_type);
		(void)fprintf(stderr, "Color: %s\n",
		    d->d_color ? "black" : "red");
		(void)fprintf(stderr, "Left child: %d\n", d->d_left_child);
		(void)fprintf(stderr, "Right child: %d\n", d->d_right_child);
		(void)fprintf(stderr, "Flags: 0x%x\n", d->d_flags);
		cdf_timestamp_to_timespec(&ts, d->d_created);
		(void)fprintf(stderr, "Created %s", cdf_ctime(&ts.tv_sec));
		cdf_timestamp_to_timespec(&ts, d->d_modified);
		(void)fprintf(stderr, "Modified %s", cdf_ctime(&ts.tv_sec));
		(void)fprintf(stderr, "Stream %d\n", d->d_stream_first_sector);
		(void)fprintf(stderr, "Size %d\n", d->d_size);
		switch (d->d_type) {
		case CDF_DIR_TYPE_USER_STORAGE:
			(void)fprintf(stderr, "Storage: %d\n", d->d_storage);
			break;
		case CDF_DIR_TYPE_USER_STREAM:
			if (sst == NULL)
				break;
			if (cdf_read_sector_chain(info, h, sat, ssat, sst,
			    d->d_stream_first_sector, d->d_size, &scn) == -1) {
				warn("Can't read stream for %s at %d len %d",
				    name, d->d_stream_first_sector, d->d_size);
				break;
			}
			cdf_dump_stream(h, &scn);
			free(scn.sst_tab);
			break;
		default:
			break;
		}

	}
}
