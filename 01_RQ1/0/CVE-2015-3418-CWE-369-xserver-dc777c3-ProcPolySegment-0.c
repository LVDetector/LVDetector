ProcPolySegment(ClientPtr client)
{
    int nsegs;
    GC *pGC;
    DrawablePtr pDraw;

    REQUEST(xPolySegmentReq);

    REQUEST_AT_LEAST_SIZE(xPolySegmentReq);
    VALIDATE_DRAWABLE_AND_GC(stuff->drawable, pDraw, DixWriteAccess);
    nsegs = (client->req_len << 2) - sizeof(xPolySegmentReq);
    if (nsegs & 4)
        return BadLength;
    nsegs >>= 3;
    if (nsegs)
        (*pGC->ops->PolySegment) (pDraw, pGC, nsegs, (xSegment *) &stuff[1]);
    return Success;
}
