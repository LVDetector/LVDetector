static void jpg_put_pixel_rows(j_decompress_ptr cinfo, jpg_dest_t *dinfo,
  JDIMENSION rows_supplied)
{
	JSAMPLE *bufptr;
	int cmptno;
	JDIMENSION x;
	uint_fast32_t width;

	JAS_DBGLOG(10, ("jpg_put_pixel_rows(%p, %p)\n", cinfo, dinfo));

	if (dinfo->error) {
		return;
	}

	assert(cinfo->output_components == jas_image_numcmpts(dinfo->image));

	for (cmptno = 0; cmptno < cinfo->output_components; ++cmptno) {
		width = jas_image_cmptwidth(dinfo->image, cmptno);
		bufptr = (dinfo->buffer[0]) + cmptno;
		for (x = 0; x < width; ++x) {
			jas_matrix_set(dinfo->data, 0, x, GETJSAMPLE(*bufptr));
			bufptr += cinfo->output_components;
		}
		JAS_DBGLOG(10, (
		  "jas_image_writecmpt called for component %d row %lu\n", cmptno,
		  JAS_CAST(unsigned long, dinfo->row)));
		if (jas_image_writecmpt(dinfo->image, cmptno, 0, dinfo->row, width, 1,
		  dinfo->data)) {
			dinfo->error = 1;
		}
	}
	dinfo->row += rows_supplied;
}
