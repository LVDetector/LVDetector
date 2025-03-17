static int __init isolated_cpu_setup(char *str)
{
	int ret;

	alloc_bootmem_cpumask_var(&cpu_isolated_map);
	ret = cpulist_parse(str, cpu_isolated_map);
	if (ret) {
		pr_err("sched: Error, all isolcpus= values must be between 0 and %d\n", nr_cpu_ids);
		return 0;
	}
	return 1;
}
