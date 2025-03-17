static int edid_size(const u8 *edid, int data_size)
{
	if (data_size < EDID_LENGTH)
		return 0;

	return (edid[0x7e] + 1) * EDID_LENGTH;
}
