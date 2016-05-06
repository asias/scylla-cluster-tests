import subprocess
import threading
import Queue
import os


class StressInfo(object):
    def __init__(self, stress_processes=1, stress_threads=10, stress_loaders=1, stress_duration=1,
                 stress_ip='127.0.0.1', current_run=1):
        self.stress_processes = stress_processes
        self.stress_threads = stress_threads
        self.stress_loaders = stress_loaders
        # minutes
        self.stress_duration = stress_duration
        self.stress_ip = stress_ip
        self.current_run = current_run

        self.max_run = 1
        self.ops_detail = {}
        self.ops_sum = {}



    def get_stress_cmd(self, duration=120, threads=100, ip='127.0.0.1'):
        return ("cassandra-stress write no-warmup cl=QUORUM duration=%sm "
                "-schema 'replication(factor=3)' -port jmx=6868 "
                "-mode cql3 native -rate threads=%s "
                "-pop seq=1..10000000 -node %s" % (duration, threads, ip))

    def run_stress_thread(self, queue, loader_idx, process_idx):
        cmd = self.get_stress_cmd(self.stress_duration, self.stress_threads, self.stress_ip)
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            shell=True,
            startupinfo=None,
        )
        print 'Running cassandra-stress run=%d loader=%d process=%d' % (self.current_run, loader_idx, process_idx)
        output, _ = process.communicate()

        queue.put(output)

    def get_ops(self, logfile):
        with open(logfile, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line.startswith('op rate'):
                    ops = line.split(':')[1].split()[0]
                    return int(ops)
        return 0

    def run_stress_on_loader(self, loader_idx):
        threads = []
        for process_idx in xrange(self.stress_processes):
            queue = Queue.Queue()
            t = threading.Thread(target=self.run_stress_thread, args=(queue, loader_idx, process_idx))
            t.setDaemon(True)
            threads.append((t, queue))
            t.start()
        idx = 0
        ops_sum = 0
        ops_detail = []
        for t, q in threads:
            lines = q.get()
            logdir = os.path.join('logs', 'loader%d' % loader_idx, 'run%d' % self.current_run)
            try:
                os.makedirs(logdir)
            except:
                pass
            logfile = os.path.join(logdir, '%d.log' % idx)
            with open(logfile, 'w') as f:
                f.write(lines)
            ops = self.get_ops(logfile)
            ops_sum += ops
            ops_detail.append(ops)
            idx += 1
            t.join()

        self.ops_sum[loader_idx] = ops_sum
        self.ops_detail[loader_idx] = ops_detail

        print "loader=%d, ops_sum=%d, ops=%s" % (loader_idx, self.ops_sum[loader_idx], self.ops_detail[loader_idx])

    def run_stress(self):
        threads = []
        for loader_idx in xrange(self.stress_loaders):
            t = threading.Thread(target=self.run_stress_on_loader, args=(loader_idx,))
            t.setDaemon(True)
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        total_ops = 0
        for ops in self.ops_sum.values():
            total_ops += ops

        print "Total ops for run=%d: %d" % (self.current_run, total_ops)


if __name__ == '__main__':
    # # run 1
    # StressInfo(stress_loaders=2, stress_processes=1, current_run=1).run_stress()

    # run 2
    StressInfo(stress_loaders=2, stress_processes=2, current_run=2).run_stress()

    # # run 3
    # StressInfo(stress_processes=3, current_run=3).run_stress()
    #
    # # run 4
    # StressInfo(stress_processes=4, current_run=4).run_stress()
    #
    # # run 5
    # StressInfo(stress_processes=5, current_run=5).run_stress()