# Use small Python standard-library helpers

Bundle narrow local helpers with the two core Skills for file enumeration,
candidate identity checks, state validation and atomic state writes. Use
Python 3.11+ with only the standard library and a user-provided interpreter;
installation of an interpreter or third-party packages is not automatic, and
no dependency manager or personal framework is a product dependency. This makes file handling
repeatable without adding a workflow engine or separate host-specific cores.
Review Only helper operations remain read-only; Full Task state writes remain
within the authorized task scope. macOS is the initial real-host validation
platform; retain portability to Windows and Linux while marking those platforms
unverified until actual evidence supports a compatibility claim.

If a suitable interpreter is unavailable, Review Only may still perform the
read-only inspection it can support, explicitly reporting input-identity,
coverage and verification gaps without claiming unperformed helper checks.
Full Task stops at the runtime prerequisite check until the user supplies a
suitable interpreter.
