AttachOffloadGPU(ScreenPtr pScreen, ScreenPtr new)
{
    assert(new->isGPU);
    xorg_list_add(&new->offload_head, &pScreen->offload_slave_list);
    new->current_master = pScreen;
}
