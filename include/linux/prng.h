/*
 * include/linux/prng.h
 */
#ifndef _LINUX_PRNG_H
#define _LINUX_PRNG_H

extern int prng_input_proc_update(const void *r, size_t size, const char *caller);
extern void prng_input_proc_stop(void);

#endif /* _LINUX_PRNG_H */

