#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

static void random_pause(void) {
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);

    // 让父子进程以不同且每次运行会变化的间隔暂停，放大调度交错现象。
    useconds_t delay = (useconds_t)((now.tv_nsec ^ getpid()) % 50000);
    usleep(delay);
}

int main(void) {
    // 关闭 stdout 缓冲，避免缓冲区复制干扰我们观察 fork 后的输出。
    setvbuf(stdout, NULL, _IONBF, 0);

    printf("fork 前：只有一个进程，pid=%d\n", getpid());

    pid_t child_pid = fork();
    if (child_pid < 0) {
        perror("fork");
        return EXIT_FAILURE;
    }

    const char *role = child_pid == 0 ? "子进程" : "父进程";

    for (int step = 1; step <= 8; step++) {
        printf("%-9s pid=%d, ppid=%d, step=%d\n",
               role, getpid(), getppid(), step);
        random_pause();
    }

    if (child_pid == 0) {
        printf("子进程结束：pid=%d\n", getpid());
        return EXIT_SUCCESS;
    }

    // waitpid 只约束这行之后的输出，不约束上面父子循环的先后顺序。
    if (waitpid(child_pid, NULL, 0) < 0) {
        perror("waitpid");
        return EXIT_FAILURE;
    }

    printf("父进程确认子进程已结束：pid=%d\n", getpid());
    return EXIT_SUCCESS;
}
