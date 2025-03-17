BOOL nsc_context_reset(NSC_CONTEXT* context, UINT32 width, UINT32 height)
{
	if (!context)
		return FALSE;

	context->width = width;
	context->height = height;
	return TRUE;
}
