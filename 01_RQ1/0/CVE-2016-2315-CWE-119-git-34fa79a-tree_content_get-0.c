static int tree_content_get(
	struct tree_entry *root,
	const char *p,
	struct tree_entry *leaf,
	int allow_root)
{
	struct tree_content *t;
	const char *slash1;
	unsigned int i, n;
	struct tree_entry *e;

	slash1 = strchrnul(p, '/');
	n = slash1 - p;
	if (!n && !allow_root)
		die("Empty path component found in input");

	if (!root->tree)
		load_tree(root);

	if (!n) {
		e = root;
		goto found_entry;
	}

	t = root->tree;
	for (i = 0; i < t->entry_count; i++) {
		e = t->entries[i];
		if (e->name->str_len == n && !strncmp_icase(p, e->name->str_dat, n)) {
			if (!*slash1)
				goto found_entry;
			if (!S_ISDIR(e->versions[1].mode))
				return 0;
			if (!e->tree)
				load_tree(e);
			return tree_content_get(e, slash1 + 1, leaf, 0);
		}
	}
	return 0;

found_entry:
	memcpy(leaf, e, sizeof(*leaf));
	if (e->tree && is_null_sha1(e->versions[1].sha1))
		leaf->tree = dup_tree_content(e->tree);
	else
		leaf->tree = NULL;
	return 1;
}
