static void nfnl_err_del(struct nfnl_err *nfnl_err)
{
	list_del(&nfnl_err->head);
	kfree(nfnl_err);
}
