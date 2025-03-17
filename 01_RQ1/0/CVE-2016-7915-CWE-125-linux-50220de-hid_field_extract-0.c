u32 hid_field_extract(const struct hid_device *hid, u8 *report,
			unsigned offset, unsigned n)
{
	if (n > 32) {
		hid_warn(hid, "hid_field_extract() called with n (%d) > 32! (%s)\n",
			 n, current->comm);
		n = 32;
	}

	return __extract(report, offset, n);
}
