from __future__ import annotations
import json,time
from pathlib import Path
class JSONLRecorder:
    def __init__(self,path): self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def append(self,event):
        with self.path.open('a',encoding='utf-8') as f: f.write(json.dumps(event,separators=(',',':'))+'\n')
