int cac_list_compare_path(const void *a, const void *b)
{
	if (a == NULL || b == NULL)
		return 1;
	return memcmp( &((cac_object_t *) a)->path,
		&((cac_object_t *) b)->path, sizeof(sc_path_t));
}
