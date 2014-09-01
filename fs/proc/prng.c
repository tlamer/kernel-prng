#include <linux/fs.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/printk.h>
#include <linux/prng.h>
#include <linux/string.h>

#define PRNG_BUFFER_SIZE 1024*1024*2

char prng_input_proc_buffer[PRNG_BUFFER_SIZE];
int prng_input_proc_offset = 0;
unsigned int prng_input_proc_on = 1;

void prng_input_proc_stop(void) {
	pr_notice("ths: stopping gathering data for /proc/prng_input");
	prng_input_proc_on = 0;
}

int prng_input_proc_update(const void *r, size_t size, const char *caller)
{
	unsigned int sz = sizeof(size_t);
	unsigned int fsz = strlen(caller) + 1;

	if (prng_input_proc_on) {
		// to avoid overflow
		if (prng_input_proc_offset + fsz + sz + sizeof(r) > PRNG_BUFFER_SIZE) {
			pr_notice("ths: the buffer is too small to store all the data");
			prng_input_proc_stop();
			return 0;
		}

		// copy function name to buffer
		strcpy(prng_input_proc_buffer + prng_input_proc_offset, caller);
		prng_input_proc_offset += fsz;

		// store data size and data itself into the buffer
		memcpy(prng_input_proc_buffer + prng_input_proc_offset, &size, sz);
		prng_input_proc_offset += sz;
		memcpy(prng_input_proc_buffer + prng_input_proc_offset, r, size);
		prng_input_proc_offset += size;
	}
	return 0;
}
EXPORT_SYMBOL(prng_input_proc_update);

static int prng_input_proc_show(struct seq_file *m, void *v)
{
	seq_write(m, prng_input_proc_buffer, sizeof(prng_input_proc_buffer));
	return 0;
}

static int prng_input_proc_open(struct inode *inode, struct file *file)
{
	return single_open(file, prng_input_proc_show, NULL);
}

static const struct file_operations prng_input_proc_fops = {
	.open		= prng_input_proc_open,
	.read		= seq_read,
	.llseek		= seq_lseek,
	.release	= single_release,
};

static int __init proc_prng_input_init(void)
{
	proc_create("prng_input", 0, NULL, &prng_input_proc_fops);
	return 0;
}
fs_initcall(proc_prng_input_init);

