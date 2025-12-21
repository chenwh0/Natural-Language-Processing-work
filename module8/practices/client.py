#!/usr/bin/env python3
"""
Q&A MCP Orchestrator Client - coordinates extractor + generator.
"""

import asyncio
import json
import subprocess
import sys
from typing import Dict, Any

class QAClient:
    def __init__(self):
        self.req_id = 0
        self.servers: Dict[str, subprocess.Popen] = {}

    def _next_id(self):
        self.req_id += 1
        return self.req_id
        
   #Standard methods to communicate with the other agents/services
    async def _send(self, proc, req):
        proc.stdin.write(json.dumps(req) + "\n")
        proc.stdin.flush()
        line = await asyncio.get_event_loop().run_in_executor(None, proc.stdout.readline)
        if not line:
            raise RuntimeError("No response from subprocess; check stderr for errors.")
        return json.loads(line.strip())

    #Standard methods connect with other services
    async def connect(self, name: str, script: str):
        #Since we are using this orchestrator to start other services, we set it up as two subprocesses
        proc = subprocess.Popen([sys.executable, script],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        self.servers[name] = proc
        print(f"Starting {name}...", file=sys.stderr)
        await asyncio.sleep(3)  # allow time to load the models, if loading of your models takes time, and if you get a timeout error, 
                                # try increasing this sleep time

        await self._send(proc, {"jsonrpc": "2.0", "id": self._next_id(),
                                "method": "initialize",
                                "params": {"protocolVersion": "2024-11-05", "capabilities": {}}})
        tools = await self._send(proc, {"jsonrpc": "2.0", "id": self._next_id(),
                                        "method": "tools/list", "params": {}})
        print(f"Connected to {name} ({[t['name'] for t in tools['result']['tools']]})")

    #Method to call the tools
    async def call_tool(self, server: str, tool: str, args: Dict[str, Any]):
        proc = self.servers[server]
        req = {"jsonrpc": "2.0", "id": self._next_id(),
               "method": "tools/call",
               "params": {"name": tool, "arguments": args}}
        res = await self._send(proc, req)
        return res["result"]["content"][0]["text"]

    async def run(self):
        #Now notice in this run method, we are calling the two agents that we created.
        await self.connect("extractor", "extractor.py")
        await self.connect("generator", "generator.py")

        #Now we create the a terminal input option to input a question.
        print("\nAsk a question (type 'quit' to exit)")
        while True:
            q = input("\nQ> ").strip()
            if q.lower() in {"quit", "exit"}:
                break

            print("Extracting relevant context...")

            #This is how we call a tool, we are calling the extractor agent , extract_info method and passing down the question
            context = await self.call_tool("extractor", "extract_info", {"question": q})

            
            print("Retrieved context snippet:")
            print(context[:300] + "..." if len(context) > 300 else context)

            print("\n Generating answer...")

            #Now that we have the context, let's call the generator to generate the answer.
            #Notice that now we call, generator agent, and generate_answer tool and passing down 
            #question and context both.

            answer = await self.call_tool("generator", "generate_answer",
                                          {"question": q, "context": context})
            print("\n Final Answer:\n" + answer)

        for p in self.servers.values():
            p.terminate()

if __name__ == "__main__":
    asyncio.run(QAClient().run())
