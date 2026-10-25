# Version-locked Blender runtime

The fresh Qwen3.8 Turbo trial uses the existing installed **Blender5.2.3 LTS**
binary at tools/blender-5.2.3-linux-x64/blender on Z6. The operator MCP transport
checks the actual executable and its queue runner; authoring also asserts the
version inside the isolated CPU sandbox. Fresh scenes contain zero objects.

Queue: var/bowling52-qwen38-turbo-20261025-r1. No old queue job may be used as an
asset source. The new guard starts with no attempts/failures and keeps all accepted
IDs durably. Retired jobs and databases remain archived, not deleted.

Source-free Stage00 is allowed after fresh reference acceptance. Later use the
machine-owned current source and poll automatic validation. The read-only native
validator and installed API/return-type catalog are unchanged tooling. Captured
API metadata may retain provenance to its original read-only capture job; it is
never an authored scene or acceptance claim for the fresh trial.
