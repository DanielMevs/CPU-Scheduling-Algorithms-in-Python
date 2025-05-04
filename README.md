# CPU Scheduling Algorithms

This repository contains implementations of various CPU scheduling algorithms used in operating systems. The code simulates how different scheduling strategies manage processes with alternating CPU and I/O bursts.

## Algorithms Implemented

- **First-Come-First-Served (FCFS)**: Processes are executed in the order they arrive
- **Shortest Job First (SJF)**: Non-preemptive algorithm that selects the process with the shortest CPU burst time
- **Round Robin (RR)**: Time-sliced algorithm where each process gets a small unit of CPU time
- **Multi-Level Feedback Queue (MLFQ)**: Combines multiple scheduling algorithms in a hierarchical structure

## Features

- Process simulation with alternating CPU and I/O bursts
- Statistics calculation (waiting time, turnaround time, response time)
- CPU utilization measurement
- Object-oriented design for easy extension

## Usage

Run the main script to see a comparison of all implemented scheduling algorithms:

```bash
python cpu_scheduler.py
```

You can also use individual schedulers in your own code:

```python
from cpu_scheduler import FCFSScheduler, create_test_processes

# Create processes
processes = create_test_processes()

# Run FCFS scheduler
scheduler = FCFSScheduler()
terminated = scheduler.schedule(processes)

# Print results
scheduler.print_results(terminated)
```

## Extending the Code

You can add new scheduling algorithms by creating a new class that inherits from the `Scheduler` base class and implements the `schedule` method. For example:

```python
class PriorityScheduler(Scheduler):
    def __init__(self):
        super().__init__("Priority Scheduler")

    def schedule(self, processes):
        # Implement priority scheduling algorithm
        # ...
        return terminated
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
