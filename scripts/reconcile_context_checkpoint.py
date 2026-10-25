"""Fixed operator/runtime entry point for safe context checkpoint reconciliation."""
import asyncio
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from scripts.context_recovery import reconcile
from scripts.submission_guard import SubmissionGuard
from scripts.workflow_tools import Workflow
import blender52_mcp as worker


async def main():
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['coding','references'],default='coding');args=parser.parse_args()
    guard=SubmissionGuard(ROOT/'.runtime/blender52/submissions.sqlite')
    client=worker.ProjectTransport('kingpomf@z6-llm',worker.REMOTE_APP,worker.REMOTE_APP+'/var/'+worker.TRIAL,worker.BINARY,str(ROOT/'artifacts/downloads'))
    print(json.dumps(await reconcile(ROOT,Workflow(ROOT,client,guard),guard,phase=args.phase)))


if __name__=='__main__':asyncio.run(main())
