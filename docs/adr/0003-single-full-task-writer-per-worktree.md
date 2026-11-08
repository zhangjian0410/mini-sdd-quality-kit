# Use one Full Task writer per worktree

V0 assumes that only one Full Task modifies code in a given worktree at a time.
Historical task records may remain, and users who need parallel implementation
provide separate worktrees themselves. This bounds candidate ownership and drift
handling without introducing a concurrent task coordinator or locking platform;
drift detection remains necessary and does not imply support for concurrent writes.
