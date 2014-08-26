#include <linux/fs.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/printk.h>
#include <linux/prng.h>
#include <linux/string.h>

#define PRNG_BUFFER_SIZE 1024*1024*5

char prng_proc_buffer[PRNG_BUFFER_SIZE];
int prng_proc_offset = 0;
unsigned int prng_proc_on = 1;

void prng_proc_stop(void) {
	pr_notice("random: stopping gathering data for /proc/prng");
	prng_proc_on = 0;
}

int prng_proc_update(const void *r, size_t size, const char *caller)
{
	unsigned int sz = sizeof(size_t);
	unsigned int fsz = strlen(caller) + 1;

	if (prng_proc_on) {
		// to avoid overflow
		if (prng_proc_offset + fsz + sz + sizeof(r) > PRNG_BUFFER_SIZE) {
			prng_proc_stop();
			return 0;
		}

		// copy function name to buffer
		strcpy(prng_proc_buffer + prng_proc_offset, caller);
		prng_proc_offset += fsz;

		// store data size and data itself into the buffer
		memcpy(prng_proc_buffer + prng_proc_offset, &size, sz);
		memcpy(prng_proc_buffer + prng_proc_offset + sz, r, sizeof(*r));
		prng_proc_offset += 4 + sz;
	}
	return 0;
}
EXPORT_SYMBOL(prng_proc_update);

static int prng_proc_show(struct seq_file *m, void *v)
{
	seq_write(m, prng_proc_buffer, sizeof(prng_proc_buffer));
	return 0;
}

static int prng_proc_open(struct inode *inode, struct file *file)
{
	return single_open(file, prng_proc_show, NULL);
}

static const struct file_operations prng_proc_fops = {
	.open		= prng_proc_open,
	.read		= seq_read,
	.llseek		= seq_lseek,
	.release	= single_release,
};

static int __init proc_prng_init(void)
{
	proc_create("prng", 0, NULL, &prng_proc_fops);
	return 0;
}
fs_initcall(proc_prng_init);

