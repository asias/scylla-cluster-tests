#scylla-6.1.2
export SCT_SCYLLA_VERSION=6.1.2
export SCT_ENABLE_ARGUS=False
#proxychains4 hydra run-test longevity_test.LongevityTest.test_custom_time --backend docker --config test-cases/PR-provision-test-docker.yaml
#proxychains4 hydra run-test performance_regression_test.PerformanceRegressionTest.test_latency_mixed_with_nemesis --backend docker --config test-cases/performance/perf-regression-latency-650gb-with-nemesis.yaml  --config configurations/tablets_disabled.yaml --config configurations/disable_kms.yaml
proxychains4 hydra run-test performance_regression_test.PerformanceRegressionTest.test_latency_write_with_nemesis --backend docker --config test-cases/performance/perf-regression-latency-650gb-with-nemesis.yaml  --config configurations/tablets_disabled.yaml --config configurations/disable_kms.yaml

# clearnup docker volume  prune
