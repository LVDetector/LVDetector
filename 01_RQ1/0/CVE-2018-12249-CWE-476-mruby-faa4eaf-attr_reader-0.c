attr_reader(mrb_state *mrb, mrb_value obj)
{
  mrb_value name = mrb_proc_cfunc_env_get(mrb, 0);
  return mrb_iv_get(mrb, obj, to_sym(mrb, name));
}
