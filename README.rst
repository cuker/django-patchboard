Short Term Queue
================
THIS MAY NOT BE A GOOD IDEA
shortstack.pk
Optimized for completing within a request cycle
Better then spawning a new thread for each item, that might eat up all resources at once (mysql connections running out, spawning 500 processes, etc)
Only optimal if allot of operations are to be done
Possibly reduce overhead by keeping everything in memory
Queue tasks have an enforced time limit (15 seconds?)
Items in the queue expire if they are not retrieved in time (45 seconds, request time limit - task item limit)
Tasks that take too long will be reported in a log
Items expiring while in the queue will be report in a log and possibly up the number of processes
If a certain number of items in the queue are at risk of expiring then possibly up the number of processes
Specify a fall back function in case of expiration. Would likely return None or raise an exception

Circuit Breaker
===============
circuitbreaker.py
Used to limit resource usage while a 3rd party is down
If X consecutive failures, open the circuit and use an exception on each call CircuitOpen
After a specified timeout, the circuit tests itself, if success, close the circuit
Unhandled exceptions count as a failure and are passed up

A task may reschedule itself for a future date if the circuit is open
Listeners determine whether to use a circuit breaker, ideal if it is hitting the wire

Signal Categories
=================

Fire and Forget
---------------
Classic use of django signals

Two possible categories of listeners:

  # Want an immediate effect, no queue
  # May be put on a queue and completed outside of the request cycle

Listeners determine if they are to be queued or not

Collectors
----------
Fires a signal and collects the responses of all the listeners.
May aggregate results, but is done on the side of the collector
Listeners may be queued, but may only use short term queue
Collector determines if listeners are to be queued
May detect the number of listeners and only default to short term queue if it is above a certain number


Signals with Side-Effects
-------------------------
prioritizeddispatcher.py
Listeners may be sharing an object they are modifying
Needs to be prioritized to guarantee to order of the side effects
Using Queues is probably not a good idea in this scenario
