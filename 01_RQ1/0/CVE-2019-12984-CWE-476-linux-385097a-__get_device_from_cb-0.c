static struct nfc_dev *__get_device_from_cb(struct netlink_callback *cb)
{
	struct nlattr **attrbuf = genl_family_attrbuf(&nfc_genl_family);
	struct nfc_dev *dev;
	int rc;
	u32 idx;

	rc = nlmsg_parse_deprecated(cb->nlh,
				    GENL_HDRLEN + nfc_genl_family.hdrsize,
				    attrbuf, nfc_genl_family.maxattr,
				    nfc_genl_policy, NULL);
	if (rc < 0)
		return ERR_PTR(rc);

	if (!attrbuf[NFC_ATTR_DEVICE_INDEX])
		return ERR_PTR(-EINVAL);

	idx = nla_get_u32(attrbuf[NFC_ATTR_DEVICE_INDEX]);

	dev = nfc_get_device(idx);
	if (!dev)
		return ERR_PTR(-ENODEV);

	return dev;
}
