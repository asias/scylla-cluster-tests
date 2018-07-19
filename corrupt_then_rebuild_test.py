#!/usr/bin/env python

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.
#
# Copyright (c) 2017 ScyllaDB

from avocado import main
from sdcm.tester import ClusterTester
from sdcm import nemesis


class CorruptThenRebuildTest(ClusterTester):
    """
    :avocado: enable
    """

    def test_corrupt_then_rebuild_nodes(self):
        # populates 100GB
        write_queue = self.populate_data_parallel(100, blocking=False)

        self.db_cluster.wait_total_space_used_per_node(50 * (1024 ** 3))  # calculates 50gb in bytes

        # run rebuild
        current_nemesis = nemesis.CorruptThenRebuildMonkey(self.db_cluster, self.loaders, self.monitors, None)
        current_nemesis.disrupt()

        for stress in write_queue:
            self.verify_stress_thread(queue=stress)
        self.populate_data_parallel(100, blocking=False, read=True)

    def test_wipe_then_rebuild_nodes(self):
        # populates 1B keys RF=3 default c-s schema
        nr_partitions = int(1e9)
        nr_partitions = int(1e6)
        write_queue = self.populate_data_parallel_nr_partitions(nr_partitions, blocking=True)

        # run rebuild
        current_nemesis = nemesis.CorruptThenRebuildMonkey(self.db_cluster, self.loaders, self.monitors, None)
        current_nemesis.disrupt()

if __name__ == '__main__':
    main()
