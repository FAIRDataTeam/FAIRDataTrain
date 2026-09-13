> **This is the Python prototype of the Train Orchestrator.** It was last changed in August 2025
> and is kept for its history; it is not being changed.
>
> Orchestrating a run across several stations is now part of the Train Handler itself, in
> **`FAIRDataTrainHandler`**: a run has a plan, an itinerary pattern and one agreement per hop,
> and both orchestrated and choreographed itineraries are the Handler's concern rather than a
> separate component's. The reasoning is recorded as ADR-013 and D1. It is not yet public.
>
> Start at **[FAIRDataTrain](https://github.com/FAIRDataTeam/FAIRDataTrain)** for what the
> ecosystem is and which components are current.
