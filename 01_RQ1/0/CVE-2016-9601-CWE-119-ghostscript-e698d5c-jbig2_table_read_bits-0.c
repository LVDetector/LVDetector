jbig2_table_read_bits(const byte *data, size_t *bitoffset, const int bitlen)
{
    uint32_t result = 0;
    uint32_t byte_offset = *bitoffset / 8;
    const int endbit = (*bitoffset & 7) + bitlen;
    const int n_proc_bytes = (endbit + 7) / 8;
    const int rshift = n_proc_bytes * 8 - endbit;
    int i;

    for (i = n_proc_bytes - 1; i >= 0; i--) {
        uint32_t d = data[byte_offset++];
        const int nshift = i * 8 - rshift;

        if (nshift > 0)
            d <<= nshift;
        else if (nshift < 0)
            d >>= -nshift;
        result |= d;
    }
    result &= ~(-1 << bitlen);
    *bitoffset += bitlen;
    return result;
}
