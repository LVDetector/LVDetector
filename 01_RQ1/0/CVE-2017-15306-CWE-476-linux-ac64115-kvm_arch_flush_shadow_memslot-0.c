void kvm_arch_flush_shadow_memslot(struct kvm *kvm,
				   struct kvm_memory_slot *slot)
{
	kvmppc_core_flush_memslot(kvm, slot);
}
