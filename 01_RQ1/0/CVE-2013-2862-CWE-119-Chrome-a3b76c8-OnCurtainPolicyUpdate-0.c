  bool OnCurtainPolicyUpdate(bool curtain_required) {
    DCHECK(context_->network_task_runner()->BelongsToCurrentThread());

#if defined(OS_MACOSX)
    if (curtain_required) {
      if (getuid() == 0) {
        Shutdown(kLoginScreenNotSupportedExitCode);
        return false;
      }
    }
#endif
    if (curtain_->required() != curtain_required) {
      LOG(INFO) << "Updated curtain policy.";
      curtain_->set_required(curtain_required);
      return true;
    }
    return false;
  }
