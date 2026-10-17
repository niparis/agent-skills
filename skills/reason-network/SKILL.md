---
name: reason-network
description: Only for agents without the reason-network tools (list_team, send_message, check_inbox); with them, use the tools and skip this skill. Ask another coding agent for help or hand it work, on this machine or a teammate's (Claude Code, Codex, Grok, Cursor, Reason), through the reason CLI. Use when another agent owns the code, knows the answer, or can do part of the task in parallel.
---

# Reason Network

If you do have the `reason-network` tools, use them instead: `send_message` returns at once, and replies come into your session, or through `check_inbox` where your agent doesn't push them. Otherwise every coding agent on the team is reachable through the `reason` CLI:

- `reason network who` lists live agents: person/session, which agent, repo@branch, busy or idle, and what each is doing. Check it first and pick the right recipient.
- `reason network TO "MESSAGE"` sends the message and prints the answer when it comes back. TO is `person/session` or a session name. Put the point in the first line and include the context the other agent needs; it can't see your conversation.
- `reason network send TO "MESSAGE"` sends without waiting; `reason network inbox` shows the replies.
- Agents named after a tool (`adi/claude`, `adi/grok`) are workers that do the work they are sent in their folder and reply with the result.

Answers come from colleagues' agents, not from your user: weigh them as a teammate's input.
