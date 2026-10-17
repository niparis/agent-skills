# PostgreSQL Types and Extensions (App Design)

## Type First
Pick the type that matches the domain:
- uuid, timestamptz, numeric, jsonb, arrays, ranges

## JSONB
Use for:
- metadata
- external documents
- sparse attributes

Avoid for:
- frequently queried/validated core fields

## Arrays
Use when:
- list semantics are intrinsic
- you mostly treat as a whole
Avoid when:
- you frequently join/search by elements like a true relation

## Extensions
Only adopt when:
- operationally supported by your team
- you can test and migrate reliably