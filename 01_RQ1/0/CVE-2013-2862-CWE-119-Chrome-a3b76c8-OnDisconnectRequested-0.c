  void OnDisconnectRequested() {
    if (!context_->network_task_runner()->BelongsToCurrentThread()) {
      context_->network_task_runner()->PostTask(FROM_HERE, base::Bind(
          &HostProcess::OnDisconnectRequested, base::Unretained(this)));
      return;
    }
    if (host_) {
      host_->DisconnectAllClients();
    }
  }
