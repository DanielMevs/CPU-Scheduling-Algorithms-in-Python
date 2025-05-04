"""
Author: Daniel Mevs
Created: 2020-03-19
Last Modified: 2025-05-03
Description: The script implements and compares four common CPU
scheduling algorithms used in operating systems: First-Come-First-Served
(FCFS), Shortest Job First (SJF), Round Robin, and Multi-Level Feedback
 Queue (MLFQ).
Version: 2.0
"""
__author__ = "Daniel Mevs"
__version__ = "2.0"


from collections import deque
from dataclasses import dataclass
from typing import List, Tuple, Deque
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


@dataclass
class Process:
    """
    Represents a process with multiple CPU and I/O burst times.
    
    Attributes:
        burst_times: List of alternating CPU and I/O burst times
        process_name: Identifier for the process
        waiting_time: Total time spent waiting
        turn_around_time: Time from arrival to completion
        response_time: Time from arrival to first execution
        current_burst_index: Index of the current burst being processed
        complete: Whether the process has completed execution
    """
    burst_times: List[int]
    process_name: str
    waiting_time: int = 0
    turn_around_time: int = 0
    response_time: int = -1
    current_burst_index: int = 0
    complete: bool = False

    @property
    def remaining_bursts(self) -> int:
        """Returns the number of remaining bursts."""
        return len(self.burst_times) - self.current_burst_index

    @property
    def current_burst(self) -> int:
        """Returns the current burst time."""
        if self.current_burst_index < len(self.burst_times):
            return self.burst_times[self.current_burst_index]
        return 0

    @property
    def total_burst_time(self) -> int:
        """Returns the total CPU burst time."""
        return sum(self.burst_times[i] for i in range(0, len(self.burst_times), 2))

    @property
    def total_io_time(self) -> int:
        """Returns the total I/O burst time."""
        return sum(self.burst_times[i] for i in range(1, len(self.burst_times), 2))

    def advance_burst(self) -> None:
        """Advances to the next burst and updates completion status."""
        self.current_burst_index += 1
        self.complete = self.current_burst_index >= len(self.burst_times)

    def reduce_current_burst(self, time: int) -> int:
        """
        Reduces the current burst by the specified time.

        Args:
            time: Amount of time to reduce from the current burst

        Returns:
            The actual time used (may be less than requested if burst completes)
        """
        if self.current_burst_index >= len(self.burst_times):
            return 0

        actual_time = min(time, self.burst_times[self.current_burst_index])
        self.burst_times[self.current_burst_index] -= actual_time

        if self.burst_times[self.current_burst_index] <= 0:
            self.advance_burst()

        return actual_time


class Scheduler:
    """Base class for CPU scheduling algorithms."""

    def __init__(self, name: str):
        """
        Initialize the scheduler.

        Args:
            name: Name of the scheduler
        """
        self.name = name
        self.time = 0
        self.cpu_util = 0

    def update_waiting_processes(self, waiting_queue: List[Process], ready_queue: Deque[Process], time_elapsed: int) -> None:
        """
        Update the waiting time for processes in the waiting queue.

        Args:
            waiting_queue: List of processes in I/O
            ready_queue: Queue of processes ready to run
            time_elapsed: Time passed in the simulation
        """
        if not waiting_queue:
            return

        # Create a copy since we'll be modifying the list
        processes_to_remove = []

        for process in waiting_queue:
            # Decrease remaining I/O time
            actual_time = process.reduce_current_burst(time_elapsed)
            process.waiting_time += actual_time

            # If I/O burst completed, move to ready queue
            if process.current_burst_index % 2 == 0:  # Now it's a CPU burst
                processes_to_remove.append(process)
                ready_queue.append(process)

        # Remove processes that moved to ready queue
        for process in processes_to_remove:
            waiting_queue.remove(process)

    def add_to_waiting(self, waiting_queue: List[Process], process: Process) -> None:
        """
        Add a process to the waiting queue.

        Args:
            waiting_queue: List of processes in I/O
            process: Process to add to waiting queue
        """
        waiting_queue.append(process)

    def print_results(self, terminated: List[Process]) -> None:
        """
        Print the scheduling results.

        Args:
            terminated: List of terminated processes
        """
        avg_wt = sum(p.waiting_time for p in terminated) / len(terminated)
        avg_tat = sum(p.turn_around_time for p in terminated) / len(terminated)
        avg_rt = sum(p.response_time for p in terminated) / len(terminated)

        logger.info(f"Scheduler: {self.name}")
        logger.info(f"Total time: {self.time}")
        logger.info(f"CPU utilization: {(self.cpu_util/self.time)*100:.2f}%")
        logger.info(f"Average waiting time: {avg_wt:.2f}")
        logger.info(f"Average turn-around time: {avg_tat:.2f}")
        logger.info(f"Average response time: {avg_rt:.2f}")

        logger.info("\nProcess details:")
        for process in terminated:
            logger.info(f"Process: {process.process_name}")
            logger.info(f"  Waiting time: {process.waiting_time}")
            logger.info(f"  Turn around time: {process.turn_around_time}")
            logger.info(f"  Response time: {process.response_time}")


class FCFSScheduler(Scheduler):
    """First-Come-First-Served scheduler implementation."""

    def __init__(self):
        """Initialize the FCFS scheduler."""
        super().__init__("First-Come-First-Served")

    def schedule(self, processes: List[Process]) -> List[Process]:
        """
        Execute the FCFS scheduling algorithm.

        Args:
            processes: List of processes to schedule

        Returns:
            List of terminated processes
        """
        self.time = 0
        self.cpu_util = 0
        ready_queue = deque(processes)
        waiting_queue = []
        terminated = []

        while ready_queue or waiting_queue:
            if not ready_queue:
                # No ready processes, advance time
                self.time += 1
                self.update_waiting_processes(waiting_queue, ready_queue, 1)
                continue

            process = ready_queue.popleft()

            # Set response time if first time running
            if process.response_time == -1:
                process.response_time = self.time

            # Execute CPU burst
            burst_time = process.current_burst
            self.time += burst_time
            self.cpu_util += burst_time
            process.advance_burst()

            # Update waiting processes
            self.update_waiting_processes(waiting_queue, ready_queue, burst_time)

            # Check if process is complete
            if process.current_burst_index >= len(process.burst_times):
                process.complete = True
                process.turn_around_time = self.time
                terminated.append(process)
            else:
                # Process has I/O burst, add to waiting queue
                self.add_to_waiting(waiting_queue, process)

        return terminated


class SJFScheduler(Scheduler):
    """Shortest Job First scheduler implementation."""

    def __init__(self):
        """Initialize the SJF scheduler."""
        super().__init__("Shortest Job First")

    def add_to_ready(self, ready_queue: Deque[Process], process: Process) -> None:
        """
        Add a process to the ready queue, sorted by burst time.

        Args:
            ready_queue: Queue of processes ready to run
            process: Process to add to ready queue
        """
        # Convert to list for sorting
        temp = list(ready_queue)
        temp.append(process)
        # Sort by current burst time
        temp.sort(key=lambda p: p.current_burst)
        # Clear and repopulate the queue
        ready_queue.clear()
        ready_queue.extend(temp)

    def schedule(self, processes: List[Process]) -> List[Process]:
        """
        Execute the SJF scheduling algorithm.

        Args:
            processes: List of processes to schedule

        Returns:
            List of terminated processes
        """
        self.time = 0
        self.cpu_util = 0
        ready_queue = deque()

        # Sort processes by first burst time before starting
        sorted_processes = sorted(processes, key=lambda p: p.current_burst)
        ready_queue.extend(sorted_processes)

        waiting_queue = []
        terminated = []

        while ready_queue or waiting_queue:
            if not ready_queue:
                # No ready processes, advance time
                self.time += 1
                self.update_waiting_processes(waiting_queue, ready_queue, 1)
                # Re-sort the ready queue
                temp = list(ready_queue)
                temp.sort(key=lambda p: p.current_burst)
                ready_queue.clear()
                ready_queue.extend(temp)
                continue

            process = ready_queue.popleft()

            # Set response time if first time running
            if process.response_time == -1:
                process.response_time = self.time

            # Execute CPU burst
            burst_time = process.current_burst
            self.time += burst_time
            self.cpu_util += burst_time
            process.advance_burst()

            # Update waiting processes
            self.update_waiting_processes(waiting_queue, ready_queue, burst_time)

            # Re-sort the ready queue after updating
            temp = list(ready_queue)
            temp.sort(key=lambda p: p.current_burst)
            ready_queue.clear()
            ready_queue.extend(temp)

            # Check if process is complete
            if process.current_burst_index >= len(process.burst_times):
                process.complete = True
                process.turn_around_time = self.time
                terminated.append(process)
            else:
                # Process has I/O burst, add to waiting queue
                self.add_to_waiting(waiting_queue, process)

        return terminated


class RoundRobinScheduler(Scheduler):
    """Round Robin scheduler implementation."""

    def __init__(self, quantum: int):
        """
        Initialize the Round Robin scheduler.

        Args:
            quantum: Time quantum for RR scheduling
        """
        super().__init__(f"Round Robin (Quantum={quantum})")
        self.quantum = quantum

    def schedule(self, processes: List[Process], start_time: int = 0,
                 start_cpu_util: int = 0) -> Tuple[List[Process], Deque[Process], int, int]:
        """
        Execute the Round Robin scheduling algorithm.

        Args:
            processes: List of processes to schedule
            start_time: Starting time for the scheduler
            start_cpu_util: Starting CPU utilization

        Returns:
            Tuple of (waiting_queue, ready_queue, time, cpu_util)
        """
        self.time = start_time
        self.cpu_util = start_cpu_util
        ready_queue = deque(processes)
        waiting_queue = []
        terminated = []

        while ready_queue or waiting_queue:
            if not ready_queue:
                # No ready processes, advance time
                self.time += 1
                self.update_waiting_processes(waiting_queue, ready_queue, 1)
                continue

            process = ready_queue.popleft()

            # Set response time if first time running
            if process.response_time == -1:
                process.response_time = self.time

            # Execute for quantum or burst completion, whichever is less
            if process.current_burst > self.quantum:
                # Use full quantum
                process.burst_times[process.current_burst_index] -= self.quantum
                self.time += self.quantum
                self.cpu_util += self.quantum
                ready_queue.append(process)  # Process back to ready queue
                self.update_waiting_processes(waiting_queue, ready_queue, self.quantum)
            else:
                # Complete this burst
                burst_time = process.current_burst
                self.time += burst_time
                self.cpu_util += burst_time
                process.advance_burst()
                self.update_waiting_processes(waiting_queue, ready_queue, burst_time)

                # Check if process is complete
                if process.current_burst_index >= len(process.burst_times):
                    process.complete = True
                    process.turn_around_time = self.time
                    terminated.append(process)
                else:
                    # Process has I/O burst, add to waiting queue
                    self.add_to_waiting(waiting_queue, process)

        # Return remaining processes for multi-level feedback queue
        return (waiting_queue, ready_queue, self.time, self.cpu_util)


class MLFQScheduler(Scheduler):
    """Multi-Level Feedback Queue scheduler implementation."""

    def __init__(self):
        """Initialize the MLFQ scheduler."""
        super().__init__("Multi-Level Feedback Queue")

    def schedule(self, processes: List[Process]) -> List[Process]:
        """
        Execute the MLFQ scheduling algorithm with three levels:
        - Level 1: Round Robin with quantum = 5
        - Level 2: Round Robin with quantum = 10
        - Level 3: FCFS

        Args:
            processes: List of processes to schedule

        Returns:
            List of terminated processes
        """
        # Level 1: RR with quantum = 5
        rr1 = RoundRobinScheduler(5)
        waiting_queue, ready_queue, time, cpu_util = rr1.schedule(processes)

        # Level 2: RR with quantum = 10
        rr2 = RoundRobinScheduler(10)
        waiting_queue, ready_queue, time, cpu_util = rr2.schedule(
            list(ready_queue), time, cpu_util
        )

        # Level 3: FCFS for remaining processes
        self.time = time
        self.cpu_util = cpu_util

        # Convert MLFQ to use proper FCFS for last level
        fcfs = FCFSScheduler()
        fcfs.time = time
        fcfs.cpu_util = cpu_util
        terminated = fcfs.schedule(list(ready_queue))

        # Update scheduler statistics
        self.time = fcfs.time
        self.cpu_util = fcfs.cpu_util

        return terminated


def create_test_processes() -> List[Process]:
    """
    Create test processes for scheduling simulation.

    Returns:
        List of Process objects
    """
    return [
        Process([5, 27, 3, 31, 5, 43, 4, 18, 6, 22, 4, 26, 3, 24, 4], 'p1'),
        Process([4, 48, 5, 44, 7, 42, 12, 37, 9, 76, 4, 41, 9, 31, 7, 43, 8], 'p2'),
        Process([8, 33, 12, 41, 18, 65, 14, 21, 4, 61, 15, 18, 14, 26, 5, 31, 6], 'p3'),
        Process([3, 35, 4, 41, 5, 45, 3, 51, 4, 61, 5, 54, 6, 82, 5, 77, 3], 'p4'),
        Process([16, 24, 17, 21, 5, 36, 16, 26, 7, 31, 13, 28, 11, 21, 6, 13, 3, 11, 4], 'p5'),
        Process([11, 22, 4, 8, 5, 10, 6, 12, 7, 14, 9, 18, 12, 24, 15, 30, 8], 'p6'),
        Process([14, 46, 17, 41, 11, 42, 15, 21, 4, 32, 7, 19, 16, 33, 10], 'p7'),
        Process([4, 14, 5, 33, 6, 51, 14, 73, 16, 87, 6], 'p8')
    ]


def main() -> None:
    """Main function to run scheduling algorithms."""
    # Create schedulers
    schedulers = [
        FCFSScheduler(),
        SJFScheduler(),
        RoundRobinScheduler(5),
        MLFQScheduler()
    ]

    # Run each scheduler and print results
    for scheduler in schedulers:
        processes = create_test_processes()
        logger.info(f"\n{'='*50}")
        logger.info(f"Running {scheduler.name} scheduler")
        logger.info(f"{'='*50}")

        if isinstance(scheduler, RoundRobinScheduler):
            # RR returns a tuple, handle differently
            waiting_queue, ready_queue, time, cpu_util = scheduler.schedule(processes)
            # Create a custom terminated list for RR
            terminated = [p for p in processes if p.complete]
            scheduler.time = time
            scheduler.cpu_util = cpu_util
            scheduler.print_results(terminated)
        else:
            # Normal scheduler
            terminated = scheduler.schedule(processes)
            scheduler.print_results(terminated)


if __name__ == '__main__':
    main()
