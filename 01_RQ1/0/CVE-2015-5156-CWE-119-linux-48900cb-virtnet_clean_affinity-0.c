static void virtnet_clean_affinity(struct virtnet_info *vi, long hcpu)
{
	int i;

	if (vi->affinity_hint_set) {
		for (i = 0; i < vi->max_queue_pairs; i++) {
			virtqueue_set_affinity(vi->rq[i].vq, -1);
			virtqueue_set_affinity(vi->sq[i].vq, -1);
		}

		vi->affinity_hint_set = false;
	}
}
