# Workshop Feedback

Hey! Thanks for putting this together. Building workshops is genuinely hard, and I wanted to share some thoughts that might help for future iterations. This is meant constructively - the content itself is solid, it's just the delivery structure that could use some scaffolding.

## What made things harder than they needed to be

**Code structure:**
- The codebase looked "half-complete" with comments and pseudo-steps, but no clear execution contract for tool calls
- No obvious schema reference for tool payload shape (`name`, `input`, `id`) and how `tool_result` feeds back to the model
- No checkpointed flow or harness to run one step at a time
- When something broke, recovery was expensive because there were no predictable handoff points

**Room dynamics:**
- Asking "is everyone fine?" in a room of 30-40 people doesn't surface real blockers - nobody wants to be the one person holding things up
- The audience had mixed experience levels, which meant some folks finished quickly while others were still trying to understand the architecture
- Time pressure + unfamiliar code + discovery-based learning is a rough combo - you can do two of those, but all three makes it feel like a scavenger hunt

**What we needed upfront:**

This is the contract that everything else depends on. Having this visible from the start would have saved a lot of reverse-engineering:

```python
# Tool call input (from model)
{
    "name": "read_file",
    "input": {"path": "foo.txt"},
    "id": "tool_abc123"
}

# Tool result (append to conversation)
{
    "role": "user",
    "content": [{
        "type": "tool_result",
        "tool_use_id": "tool_abc123",
        "content": "file contents here",
        "is_error": False  # optional
    }]
}
```

## Why this was hard (the pedagogy)

### Cognitive load

People have limited working memory. When learning something new, that memory gets split between:
- **Intrinsic load**: the actual concept you're trying to teach (tool call contracts, agent loops)
- **Extraneous load**: navigating unfamiliar code, figuring out file structure, debugging environment issues

When extraneous load is high, there's no room left for the intrinsic stuff. The learner spends all their mental energy on "where is this defined?" and "what shape is this object?" instead of "how does an agent loop work?"

The fix is to minimize extraneous load by giving people the map upfront - file structure, data shapes, expected outputs - so they can focus on the actual concepts.

### Productive struggle vs. unproductive flailing

There's a difference between:
- **Productive struggle**: "I understand what I'm trying to do, but I need to figure out how" - this builds understanding
- **Unproductive flailing**: "I don't know what I'm trying to do, what success looks like, or where to start" - this just burns time and confidence

Discovery-based learning works when the map is known but the territory is new. Here, both the map (architecture) and the territory (data shapes) were unknown, so people spent their limited time reverse-engineering structure instead of building understanding.

### Time pressure amplifies everything

Under time pressure, people can't afford to be stuck. Every minute spent confused is a minute not learning. This makes the failure mode really punishing - if you fall behind early, you stay behind, and the gap widens as the workshop progresses.

Scaffolded steps with escape hatches let people recover. If you're stuck on step 2, you can grab the solution and rejoin at step 3 without losing the rest of the workshop.

### Social dynamics of "is everyone okay?"

Asking an open room "is everyone fine?" almost never surfaces problems because:
- Nobody wants to be the one person holding up 40 others
- People don't know if their confusion is "normal" or if they're uniquely lost
- Admitting you're stuck feels like admitting you're slow

Hand raises flip this dynamic - "raise your hand if you're still on step 2" makes it okay to be behind because you can see others are too. It also gives the presenter actual data instead of silence.

## Suggestions for next time

### 1. Step-based, file-based flow

Deliver the workshop in small incremental files so each step is runnable and recoverable:

| Step | File | Goal |
|------|------|------|
| 0 | `step_00_contract.py` | Define the tool call contract, show a valid `ToolUseBlock` payload |
| 1 | `step_01_execute_tool.py` | Implement `execute_tool` in isolation, validate unknown tool handling |
| 2 | `step_02_tool_schema.py` | Confirm tool metadata generation works |
| 3 | `step_03_single_loop.py` | One-pass: model call → tool execution → append result |
| 4 | `step_04_full_loop.py` | Wire the complete agent loop |
| 5 | `step_05_all_tools.py` | Enable all tools with happy path + failure mode checks |

Each step file should include:
- File under test
- Behavior goal
- Input sample
- Expected console output
- A "done check" at the bottom that prints OK

### 2. Better room check-ins

Instead of "is everyone fine?":
- **Hand raises**: "Raise your hand if you're still on step 2" - gives you a visual read
- **Catchup escape hatch**: Provide a `solutions/` folder so stuck people can copy-paste forward and stay with the group
- **Explicit skip points**: "If you're stuck, grab `step_03_solution.py` and we'll explain it together"

### 3. State target audience

A quick pre-flight at the start helps set expectations: "This assumes you're comfortable with Python async, basic API calls, and have used Claude's API before."

## Why this structure works

**Reduces cognitive load**: When learners know the file structure, data shapes, and expected outputs upfront, they can spend their mental energy on the actual concepts instead of reverse-engineering the codebase.

**Enables productive struggle**: Each step has a clear goal and success criteria. Learners know what they're trying to do, so when they get stuck, they're stuck on the *how*, not the *what*. That's where learning happens.

**Makes recovery cheap**: When someone falls behind, they can grab the solution for the current step and rejoin the group. They might not have written that code themselves, but they can still follow along and learn from the remaining steps. Without this, falling behind means losing the rest of the workshop.

**Works for mixed audiences**: Fast learners can skip ahead or help others. Slower learners can use the escape hatches without shame. Everyone stays roughly together, which means the presenter's explanations stay relevant to the room.

**Gives the presenter real feedback**: Hand raises and step-based check-ins surface actual progress instead of awkward silence. You can see "okay, 80% of the room is past step 3" and adjust pacing accordingly.

---

Again, the material itself is good - this is just about making it more accessible to a mixed-level room. Hope this is useful for the next iteration!
