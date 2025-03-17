static void srpt_send_done(struct ib_cq *cq, struct ib_wc *wc)
{
	struct srpt_rdma_ch *ch = cq->cq_context;
	struct srpt_send_ioctx *ioctx =
		container_of(wc->wr_cqe, struct srpt_send_ioctx, ioctx.cqe);
	enum srpt_command_state state;

	state = srpt_set_cmd_state(ioctx, SRPT_STATE_DONE);

	WARN_ON(state != SRPT_STATE_CMD_RSP_SENT &&
		state != SRPT_STATE_MGMT_RSP_SENT);

	atomic_inc(&ch->sq_wr_avail);

	if (wc->status != IB_WC_SUCCESS) {
		pr_info("sending response for ioctx 0x%p failed"
			" with status %d\n", ioctx, wc->status);

		atomic_dec(&ch->req_lim);
		srpt_abort_cmd(ioctx);
		goto out;
	}

	if (state != SRPT_STATE_DONE) {
		srpt_unmap_sg_to_ib_sge(ch, ioctx);
		transport_generic_free_cmd(&ioctx->cmd, 0);
	} else {
		pr_err("IB completion has been received too late for"
		       " wr_id = %u.\n", ioctx->ioctx.index);
	}

out:
	while (!list_empty(&ch->cmd_wait_list) &&
	       srpt_get_ch_state(ch) == CH_LIVE &&
	       (ioctx = srpt_get_send_ioctx(ch)) != NULL) {
		struct srpt_recv_ioctx *recv_ioctx;

		recv_ioctx = list_first_entry(&ch->cmd_wait_list,
					      struct srpt_recv_ioctx,
					      wait_list);
		list_del(&recv_ioctx->wait_list);
		srpt_handle_new_iu(ch, recv_ioctx, ioctx);
	}
}
