static void dump_invalid_creds(const struct cred *cred, const char *label,
			       const struct task_struct *tsk)
{
	printk(KERN_ERR "CRED: %s credentials: %p %s%s%s\n",
	       label, cred,
	       cred == &init_cred ? "[init]" : "",
	       cred == tsk->real_cred ? "[real]" : "",
	       cred == tsk->cred ? "[eff]" : "");
	printk(KERN_ERR "CRED: ->magic=%x, put_addr=%p\n",
	       cred->magic, cred->put_addr);
	printk(KERN_ERR "CRED: ->usage=%d, subscr=%d\n",
	       atomic_read(&cred->usage),
	       read_cred_subscribers(cred));
	printk(KERN_ERR "CRED: ->*uid = { %d,%d,%d,%d }\n",
	       cred->uid, cred->euid, cred->suid, cred->fsuid);
	printk(KERN_ERR "CRED: ->*gid = { %d,%d,%d,%d }\n",
	       cred->gid, cred->egid, cred->sgid, cred->fsgid);
#ifdef CONFIG_SECURITY
	printk(KERN_ERR "CRED: ->security is %p\n", cred->security);
	if ((unsigned long) cred->security >= PAGE_SIZE &&
	    (((unsigned long) cred->security & 0xffffff00) !=
	     (POISON_FREE << 24 | POISON_FREE << 16 | POISON_FREE << 8)))
		printk(KERN_ERR "CRED: ->security {%x, %x}\n",
		       ((u32*)cred->security)[0],
		       ((u32*)cred->security)[1]);
#endif
}
