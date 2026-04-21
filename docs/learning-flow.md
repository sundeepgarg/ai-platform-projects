# Learning Flow Notes

## 1. Request Entry

The request enters through FastAPI and receives a `request_id`.

Why it matters:

- every request should be traceable
- support teams need correlation data
- observability starts at the edge

## 2. Guardrails

Guardrails run before retrieval and before the model call.

This project demonstrates:

- simple deny-list checks
- secret-pattern detection
- basic prompt length validation

In a real platform, this layer is where you would add:

- PII checks
- jailbreak detection
- policy enforcement
- audit rules

## 3. Retrieval

The retriever loads platform documents and performs lightweight lexical scoring.

Why lexical search first:

- easy to understand
- easy to debug
- enough to learn the flow before adding vector infrastructure

## 4. Prompt Building

The platform combines:

- system intent
- prompt version
- user question
- retrieved context

This is the transition point between platform logic and model logic.

## 5. Provider Execution

The provider interface hides runtime details from the rest of the platform.

That means the API layer does not care whether the answer comes from:

- a mock provider
- Amazon Bedrock
- a future provider

## 6. Response Packaging

The response returns:

- answer
- sources
- guardrail outcome
- provider metadata
- trace steps

This is very useful for learning, debugging, and demonstrating platform thinking.

