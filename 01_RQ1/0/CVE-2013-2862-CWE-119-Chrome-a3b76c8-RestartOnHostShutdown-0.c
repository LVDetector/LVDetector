  void RestartOnHostShutdown() {
    DCHECK(context_->network_task_runner()->BelongsToCurrentThread());

    if (shutting_down_)
      return;

    restarting_ = false;
    host_ = NULL;
    ResetHost();

    StartHost();
  }
