---
name: capture
description: Capture an in-session insight to the Wayfinder capture markers sidecar.
---

When the user invokes `/capture`, run a short structured interview and append a capture marker to the per-session sidecar file.

## When to use

Use `/capture` when the user wants to mark an assistant message or add richer metadata (method/theme/notes) to an insight. For quick user-only thoughts, the inline `#insight: ...` tag is preferred.

## Interview flow

Ask **one question at a time**. Do not ask all questions at once.

1. **Summary** (required)  
   "用一句话总结这条经验："  
   - If the user replies with empty text, "取消", "cancel", or "skip", stop and do not write a marker.

2. **Method dimension** (optional)  
   "方法维度？可选：task_definition / method_selection / scope_tradeoff / context_injection / prompt_refinement / constraint_declaration / course_correction / acceptance_termination。不需要就回复 skip。"  
   - If skipped, set `method_tag` to `null`.

3. **Theme tag** (optional)  
   "主题标签？可选：engine / ui / state_management / testing / build_tooling / documentation / planning。不需要就回复 skip，也可自定义。"  
   - If skipped, set `theme_tag` to `null`.

4. **Reviewer notes** (optional)  
   "需要给审核者留备注或限制说明吗？不需要就回复 skip。"

5. **Anchor confirmation**  
   "将标记到上一条 assistant 消息。要改为当前 user 消息，还是保持？"  
   - Default `anchor_target` is `previous_assistant`.  
   - If the user says "user", set `anchor_target` to `current_user`.  
   - If the user says "skip" or "none", set `anchor_target` to `unspecified`.  
   - If the user cancels, stop.

## Writing the marker

1. Create a temporary JSON input file at `~/.claude/capture-draft.json` with keys:
   - `summary` (string, required)
   - `method_tag` (string or null)
   - `theme_tag` (string or null)
   - `notes` (string)
   - `anchor_target` (string)

2. Run the helper:
   ```bash
   python "$HOME/.claude/skills/capture/capture_helper.py" append --json-file "$HOME/.claude/capture-draft.json"
   ```

3. Read the helper output. If it reports success, tell the user:
   - the generated `marker_id`
   - the sidecar file path
   - that the marker will be resolved against the session transcript by `extract_capture_markers.py`

4. Delete the temporary draft file after the helper succeeds.

## Error handling

- If the helper reports "Could not find project root", tell the user: "当前目录不在经验包项目内。请切换到项目根目录，或使用 `#insight` 在消息里标记。"
- If `CLAUDE_CODE_SESSION_ID` is missing, tell the user: "无法获取当前 session ID，请确认你是在 Claude Code 会话中调用 `/capture`。"
- If the user cancels at any step, do not run the helper and do not write anything.

## Privacy

The helper performs light scrubbing on `summary` and `notes` before writing (home/project paths + common secret patterns). Full scrubbing happens later via `scripts/scrubber.py`.
