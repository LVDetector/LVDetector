no_ci_flags(OM_uint32 *minor_status,
            gss_cred_id_t *cred_handle,
            const gss_OID desired_oid,
            const gss_buffer_t value)
{
    krb5_gss_cred_id_t cred;

    cred = (krb5_gss_cred_id_t) *cred_handle;
    cred->suppress_ci_flags = 1;

    *minor_status = 0;
    return GSS_S_COMPLETE;
}
