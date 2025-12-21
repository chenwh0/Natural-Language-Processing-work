#generator.py
"""
Generator MCP Server - uses FLAN-T5-small to generate answers.
"""

import asyncio
import json
import sys
import torch
from transformers import pipeline
from typing import Any, Dict, List

sys.stdout.reconfigure(line_buffering=True)

class GeneratorServer:
    def __init__(self):
        print("Loading FLAN-T5-small.", file=sys.stderr)
        self.llm = pipeline(
            "text2text-generation",
            model="google/flan-t5-small",
            device=0 if torch.cuda.is_available() else -1
        )
        print("Generator ready!", file=sys.stderr)

    def get_server_info(self) -> Dict[str, Any]:
        return {"name": "generator-server", "version": "2.0.1"}

    #Defining the structure of the tool generate_answer
    def get_tools(self) -> List[Dict[str, Any]]:
        return [{
            "name": "generate_answer",
            "description": "Generate a concise answer using FLAN-T5-small given question + context.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "context": {"type": "string"}
                },
                "required": ["question", "context"]
            }
        }]

    #Method to call the tool
    def call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name != "generate_answer":
            raise ValueError(f"Unknown tool: {name}")
        return self._generate(args)

    #_generate the answer using the given context
    def _generate(self, args: Dict[str, Any]) -> Dict[str, Any]:
        #Arguments passed by the service caller contains the information needed in this context "question" and "context"
        q, ctx = args["question"], args["context"]
        prompt = f"Answer the question based on context.\n\nContext:\n{ctx}\n\nQuestion: {q}\nAnswer:"
        out = self.llm(prompt, max_length=200, num_return_sequences=1)[0]["generated_text"]
        return {"content": [{"type": "text", "text": out}]}

async def main():
    #Creation of the generator agent as seperate server
    srv = GeneratorServer()
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            req = json.loads(line.strip())
            if req["method"] == "initialize":
                res = {"jsonrpc":"2.0","id":req["id"],
                       "result":{"protocolVersion":"2024-11-05",
                                 "capabilities":{},
                                 "serverInfo":srv.get_server_info()}}
            elif req["method"] == "tools/list":
                res = {"jsonrpc":"2.0","id":req["id"],
                       "result":{"tools":srv.get_tools()}}
            elif req["method"] == "tools/call":
                name=req["params"]["name"]
                args=req["params"]["arguments"]
                result=srv.call_tool(name,args)
                res={"jsonrpc":"2.0","id":req["id"],"result":result}
            else:
                res={"jsonrpc":"2.0","id":req["id"],
                     "error":{"code":-32601,"message":"Unknown method"}}
            print(json.dumps(res),flush=True)
        except Exception as e:
            print(json.dumps({"jsonrpc":"2.0","id":None,
                              "error":{"code":-32603,"message":str(e)}}),flush=True)

if __name__=="__main__":
    asyncio.run(main())
