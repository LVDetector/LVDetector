BackSpace()
{
  if (curr->w_x > 0)
    {
      curr->w_x--;
    }
  else if (curr->w_wrap && curr->w_y > 0)
    {
      curr->w_x = cols - 1;
      curr->w_y--;
    }
  LGotoPos(&curr->w_layer, curr->w_x, curr->w_y);
}
