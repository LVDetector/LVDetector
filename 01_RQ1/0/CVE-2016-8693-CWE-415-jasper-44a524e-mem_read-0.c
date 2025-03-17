static int mem_read(jas_stream_obj_t *obj, char *buf, int cnt)
{
	int n;
	assert(cnt >= 0);
	assert(buf);
	jas_stream_memobj_t *m = (jas_stream_memobj_t *)obj;
	n = m->len_ - m->pos_;
	cnt = JAS_MIN(n, cnt);
	memcpy(buf, &m->buf_[m->pos_], cnt);
	m->pos_ += cnt;
	return cnt;
}
