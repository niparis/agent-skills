# [Module/File Name]

**Path:** `src/path/to/file.ext`  
**Last Verified:** [Date or commit hash]  
**Purpose:** [1–2 sentence summary]

## Overview
[What this module does, why it exists, and how it fits into the system]

## When to use
- [Primary use cases]

## When not to use
- [Common misuses or constraints]

## Public API

### `functionName(param1, param2)`
**Purpose:** [What it does]

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| param1 | string | Yes | Description |
| param2 | number | No | Description (default if any) |

**Returns:** `Promise<Type>` – Description

**Throws:**
- `ErrorType` – Condition

**Example:**
```js
const result = await functionName("value", 42);
```

**Notes:**
- Edge cases
- Performance considerations
- Async / concurrency behavior

## Implementation Notes
[Algorithms, patterns, known limitations, TODOs]

## Testing
**Test file:** `tests/path/to/file.test.ext`  
**Coverage:** [If known]  
**Run:** `npm test path/to/file`

## Evidence Sources
- [ ] Code inspection
- [ ] Tests reviewed
- [ ] Runtime behavior
- [ ] Assumption

## Unknown / Unverified
- [ ] Item requiring confirmation
- [ ] How to verify
