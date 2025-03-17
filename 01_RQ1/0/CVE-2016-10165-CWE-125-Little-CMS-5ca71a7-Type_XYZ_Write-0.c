cmsBool  Type_XYZ_Write(struct _cms_typehandler_struct* self, cmsIOHANDLER* io, void* Ptr, cmsUInt32Number nItems)
{
    return _cmsWriteXYZNumber(io, (cmsCIEXYZ*) Ptr);

    cmsUNUSED_PARAMETER(nItems);
    cmsUNUSED_PARAMETER(self);
}
