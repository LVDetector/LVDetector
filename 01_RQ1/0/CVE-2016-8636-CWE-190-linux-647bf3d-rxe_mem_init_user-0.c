int rxe_mem_init_user(struct rxe_dev *rxe, struct rxe_pd *pd, u64 start,
		      u64 length, u64 iova, int access, struct ib_udata *udata,
		      struct rxe_mem *mem)
{
	int			entry;
	struct rxe_map		**map;
	struct rxe_phys_buf	*buf = NULL;
	struct ib_umem		*umem;
	struct scatterlist	*sg;
	int			num_buf;
	void			*vaddr;
	int err;

	umem = ib_umem_get(pd->ibpd.uobject->context, start, length, access, 0);
	if (IS_ERR(umem)) {
		pr_warn("err %d from rxe_umem_get\n",
			(int)PTR_ERR(umem));
		err = -EINVAL;
		goto err1;
	}

	mem->umem = umem;
	num_buf = umem->nmap;

	rxe_mem_init(access, mem);

	err = rxe_mem_alloc(rxe, mem, num_buf);
	if (err) {
		pr_warn("err %d from rxe_mem_alloc\n", err);
		ib_umem_release(umem);
		goto err1;
	}

	WARN_ON(!is_power_of_2(umem->page_size));

	mem->page_shift		= ilog2(umem->page_size);
	mem->page_mask		= umem->page_size - 1;

	num_buf			= 0;
	map			= mem->map;
	if (length > 0) {
		buf = map[0]->buf;

		for_each_sg(umem->sg_head.sgl, sg, umem->nmap, entry) {
			vaddr = page_address(sg_page(sg));
			if (!vaddr) {
				pr_warn("null vaddr\n");
				err = -ENOMEM;
				goto err1;
			}

			buf->addr = (uintptr_t)vaddr;
			buf->size = umem->page_size;
			num_buf++;
			buf++;

			if (num_buf >= RXE_BUF_PER_MAP) {
				map++;
				buf = map[0]->buf;
				num_buf = 0;
			}
		}
	}

	mem->pd			= pd;
	mem->umem		= umem;
	mem->access		= access;
	mem->length		= length;
	mem->iova		= iova;
	mem->va			= start;
	mem->offset		= ib_umem_offset(umem);
	mem->state		= RXE_MEM_STATE_VALID;
	mem->type		= RXE_MEM_TYPE_MR;

	return 0;

err1:
	return err;
}
