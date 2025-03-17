static char *super_fgets_w(char **b, int *blen, Image *file)
{
  int
    c,
    len;

  unsigned char
    *p,
    *q;

  len=*blen;
  p=(unsigned char *) (*b);
  for (q=p; ; q++)
  {
    c=ReadBlobLSBSignedShort(file);
    if ((c == -1) || (c == '\n'))
      break;
   if (EOFBlob(file))
      break;
   if ((q-p+1) >= (int) len)
      {
        int
          tlen;

        tlen=q-p;
        len<<=1;
        p=(unsigned char *) ResizeQuantumMemory(p,(size_t) (len+2),sizeof(*p));
        *b=(char *) p;
        if (p == (unsigned char *) NULL)
          break;
        q=p+tlen;
      }
    *q=(unsigned char) c;
  }
  *blen=0;
  if ((*b) != (char *) NULL)
    {
      int
        tlen;

      tlen=q-p;
      if (tlen == 0)
        return (char *) NULL;
      p[tlen] = '\0';
      *blen=++tlen;
    }
  return((char *) p);
}
