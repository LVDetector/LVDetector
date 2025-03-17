WebGLRenderingContextBaseMap& ForciblyEvictedContexts() {
  DEFINE_THREAD_SAFE_STATIC_LOCAL(
      ThreadSpecific<Persistent<WebGLRenderingContextBaseMap>>,
      forcibly_evicted_contexts, ());
  Persistent<WebGLRenderingContextBaseMap>&
      forcibly_evicted_contexts_persistent = *forcibly_evicted_contexts;
  if (!forcibly_evicted_contexts_persistent) {
    forcibly_evicted_contexts_persistent = new WebGLRenderingContextBaseMap();
    forcibly_evicted_contexts_persistent.RegisterAsStaticReference();
  }
  return *forcibly_evicted_contexts_persistent;
}
