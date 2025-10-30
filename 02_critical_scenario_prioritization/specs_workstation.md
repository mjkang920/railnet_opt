=== OS ===
platform: Linux-6.14.0-29-generic-x86_64-with-glibc2.39
system: Linux
release: 6.14.0-29-generic
version: #29~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC Thu Aug 14 16:52:50 UTC 2
machine: x86_64

=== Python ===
python: 3.11.13 (main, Jun  5 2025, 13:12:00) [GCC 11.2.0]

=== CPU ===
Architecture:                            x86_64
CPU op-mode(s):                          32-bit, 64-bit
Address sizes:                           46 bits physical, 48 bits virtual
Byte Order:                              Little Endian
CPU(s):                                  48
On-line CPU(s) list:                     0-47
Vendor ID:                               GenuineIntel
Model name:                              Intel(R) Xeon(R) Gold 6126 CPU @ 2.60GHz
CPU family:                              6
Model:                                   85
Thread(s) per core:                      2
Core(s) per socket:                      12
Socket(s):                               2
Stepping:                                4
CPU(s) scaling MHz:                      29%
CPU max MHz:                             3700.0000
CPU min MHz:                             1000.0000
BogoMIPS:                                5200.00
Flags:                                   fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc art arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch cpuid_fault epb cat_l3 cdp_l3 pti intel_ppin ssbd mba ibrs ibpb stibp tpr_shadow flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 hle avx2 smep bmi2 erms invpcid rtm cqm mpx rdt_a avx512f avx512dq rdseed adx smap clflushopt clwb intel_pt avx512cd avx512bw avx512vl xsaveopt xsavec xgetbv1 xsaves cqm_llc cqm_occup_llc cqm_mbm_total cqm_mbm_local dtherm ida arat pln pts hwp hwp_act_window hwp_epp hwp_pkg_req vnmi pku ospke md_clear flush_l1d arch_capabilities
Virtualization:                          VT-x
L1d cache:                               768 KiB (24 instances)
L1i cache:                               768 KiB (24 instances)
L2 cache:                                24 MiB (24 instances)
L3 cache:                                38.5 MiB (2 instances)
NUMA node(s):                            2
NUMA node0 CPU(s):                       0-11,24-35
NUMA node1 CPU(s):                       12-23,36-47
Vulnerability Gather data sampling:      Vulnerable
Vulnerability Ghostwrite:                Not affected
Vulnerability Indirect target selection: Not affected
Vulnerability Itlb multihit:             KVM: Mitigation: Split huge pages
Vulnerability L1tf:                      Mitigation; PTE Inversion; VMX conditional cache flushes, SMT vulnerable
Vulnerability Mds:                       Mitigation; Clear CPU buffers; SMT vulnerable
Vulnerability Meltdown:                  Mitigation; PTI
Vulnerability Mmio stale data:           Mitigation; Clear CPU buffers; SMT vulnerable
Vulnerability Reg file data sampling:    Not affected
Vulnerability Retbleed:                  Mitigation; IBRS
Vulnerability Spec rstack overflow:      Not affected
Vulnerability Spec store bypass:         Mitigation; Speculative Store Bypass disabled via prctl
Vulnerability Spectre v1:                Mitigation; usercopy/swapgs barriers and __user pointer sanitization
Vulnerability Spectre v2:                Mitigation; IBRS; IBPB conditional; STIBP conditional; RSB filling; PBRSB-eIBRS Not affected; BHI Not affected
Vulnerability Srbds:                     Not affected
Vulnerability Tsx async abort:           Mitigation; Clear CPU buffers; SMT vulnerable

=== Memory ===
total        used        free      shared  buff/cache   available
Mem:           125Gi       7.6Gi       112Gi        11Mi       6.0Gi       117Gi
Swap:           15Gi        73Mi        15Gi

=== GPU ===
Thu Oct 30 18:40:06 2025       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 580.82.07              Driver Version: 580.82.07      CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA TITAN RTX               On  |   00000000:17:00.0 Off |                  N/A |
| 40%   35C    P8             18W /  280W |       1MiB /  24576MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
|   1  NVIDIA TITAN RTX               On  |   00000000:D5:00.0 Off |                  N/A |
| 41%   36C    P8             17W /  280W |       1MiB /  24576MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+

=== Gurobi ===
gurobi_cl: Gurobi Optimizer version 12.0.2 build v12.0.2rc0 (linux64 - "Ubuntu 24.04.3 LTS")
Copyright (c) 2025, Gurobi Optimization, LLC
gurobipy: (12, 0, 2)

=== Key Python packages ===
{
  "numpy": "2.0.1",
  "scipy": "1.16.0",
  "networkx": "3.5",
  "matplotlib": "3.10.6",
  "tqdm": "4.67.1",
  "deap": "1.4",
  "pandas": "not installed",
  "psutil": "7.0.0"
}