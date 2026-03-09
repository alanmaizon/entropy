# Entropy – Agents

## Overview

Entropy uses a **generator–critic** multi-agent pattern.
Agents are stateless async workers that communicate via structured
`AgentMessage` objects.

## ExplorerAgent

**Role**: Generate hypotheses by exploring the knowledge space.

**Input**: `AgentMessage` with `content["topic"]` (str)

**Process**:
1. Embeds the topic query
2. Retrieves relevant context from vector memory
3. Prompts the LLM to propose a hypothesis

**Output**: `AgentMessage` with `content["hypothesis"]` (dict)

## CriticAgent

**Role**: Evaluate hypotheses for logical consistency and evidential support.

**Input**: `AgentMessage` with `content["hypothesis"]` (dict)

**Process**:
1. Embeds the hypothesis statement
2. Retrieves supporting/contradicting evidence from vector memory
3. Prompts the LLM to score and verdict the hypothesis

**Output**: `AgentMessage` with `content["critique"]` (dict)

## Communication Protocol

```python
class AgentMessage(BaseModel):
    sender: str       # name of the sending agent
    recipient: str    # name of the target agent
    content: dict     # structured payload
```

## Future Agents

| Agent              | Role                                          |
|--------------------|-----------------------------------------------|
| SynthesizerAgent   | Merge related hypotheses into higher-order theories |
| RetrieverAgent     | Specialised multi-hop graph retrieval         |
| PlannerAgent       | Schedule exploration of knowledge gaps        |
