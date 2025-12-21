#extractor.py
"""
Extractor MCP Server - loads SQuAD dataset and performs semantic retrieval.
"""

import asyncio
import json
import sys
import numpy as np
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from typing import Any, Dict, List

sys.stdout.reconfigure(line_buffering=True)

class ExtractorServer:
    def __init__(self):
        print("Loading SQuAD dataset (first 100 rows)", file=sys.stderr)
        #To keep this lightweight we will only use the first 100 rows of the dataset
        dataset = load_dataset("squad", split="train[:100]")
        
        self.documents = [{"title": row["title"], "context": row["context"]} for row in dataset]

        print("Loading embedding model", file=sys.stderr)
        #Using the embedding model "all-MiniLM-L6-v2"
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        
        self.doc_embeddings = self.encoder.encode(
            [d["context"] for d in self.documents],
            show_progress_bar=False, 
            convert_to_numpy=True
        )
        print("Extractor ready with (100 docs embedded)", file=sys.stderr)

    #Define Server info 
    def get_server_info(self) -> Dict[str, Any]:
        return {"name": "extractor-server", "version": "2.0.1"}

    #Defining the extraction of relevant data as a tool. These agents use a variety of tools to conduct their operation
    #We name this tool "extract_info"
    #Other agents can call this method and find out what tools this agent has.
    def get_tools(self) -> List[Dict[str, Any]]:
        return [{
            "name": "extract_info",
            "description": "Performs semantic retrieval using embedded SQuAD contexts.",
            "inputSchema": {
                "type": "object",
                "properties": {"question": {"type": "string"}},
                "required": ["question"]
            }
        }]

    #Defining the call_tool method
    #If other agents want to use this agent, they can call this method, 
    #and specify that they need to use "extract_info" method and give the inputs that it asks.
    def call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name != "extract_info":
            raise ValueError(f"Unknown tool: {name}")
        return self._extract_info(args)

    #Defining the _extract_info method
    #This is the actual action that the method will execute

    def _extract_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        #For a given question it will find the top k related documents.
        q = args["question"]
        q_emb = self.encoder.encode([q], convert_to_numpy=True)[0]
        sims = np.dot(self.doc_embeddings, q_emb)
        top = np.argsort(sims)[-3:][::-1]

        docs = [self.documents[i] for i in top]
        combined = "\n\n".join([f"{i+1}. {d['context']}" for i, d in enumerate(docs)])
        #Notice that how we format these responses. This is a Standard Structure in MCPs. 
        #So that different agents can communicate using these standard data structures.
        return {"content": [{"type": "text", "text": combined}]} 

async def main():
    #Creating extractor agent as a server
    srv = ExtractorServer()

    #Now, the following part is about setting up the server.
    #Most of the following code is standard practice.
    #This specify the structure of input and output structures, so that any other agent can discover this service and call the methods/tools
    #MCP protocol use jsonrpc as the underlying commuincation protocol.
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            req = json.loads(line.strip())
            if req["method"] == "initialize":
                res = {"jsonrpc": "2.0","id": req["id"],
                       "result": {"protocolVersion": "2024-11-05",
                                  "capabilities": {},
                                  "serverInfo": srv.get_server_info()}}
            elif req["method"] == "tools/list":
                res = {"jsonrpc": "2.0","id": req["id"],
                       "result": {"tools": srv.get_tools()}}
            elif req["method"] == "tools/call":
                name = req["params"]["name"]
                args = req["params"]["arguments"]
                result = srv.call_tool(name, args)
                res = {"jsonrpc": "2.0","id": req["id"],"result": result}
            else:
                res = {"jsonrpc": "2.0","id": req["id"],
                       "error": {"code": -32601,"message": "Unknown method"}}
            print(json.dumps(res), flush=True)
        except Exception as e:
            print(json.dumps({"jsonrpc": "2.0","id": None,
                              "error": {"code": -32603,"message": str(e)}}), flush=True)

if __name__ == "__main__":
    #Note, that this server can be run alone, independent of other agents or services.
    asyncio.run(main())
