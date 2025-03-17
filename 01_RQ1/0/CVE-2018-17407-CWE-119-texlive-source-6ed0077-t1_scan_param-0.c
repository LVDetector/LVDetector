static void t1_scan_param(void)
{
    static const char *lenIV = "/lenIV";
    if (!t1_scan || *t1_line_array != '/')
        return;
    if (t1_prefix(lenIV)) {
        t1_lenIV = t1_scan_num(t1_line_array + strlen(lenIV), 0);
        if (t1_lenIV < 0)
            pdftex_fail("negative value of lenIV is not supported");
        return;
    }
    t1_scan_keys();
}
