# Project Interaction Style

Use this contract for every user-visible explanation in a project. The style is
saved in that project's `project_rules.yaml`, so two projects can teach in two
different ways without changing a global account setting.

## Default

If the project has no `interaction_style` section, assume the user is a newcomer to
the subject. Explain specialist choices in plain language, include a small
example or analogy when it helps, and say why the choice prevents a likely
problem. The AI chooses the recommended path; the explanation is information,
not a request for the user to choose.

For example, instead of “启用幂等键”，say: “同一条指令如果网络卡住后重试，
可能会重复创建两份任务；幂等键像快递单号，系统能认出这是同一件事，
所以只保留一份。”

## Project settings

```yaml
interaction_style:
  audience: beginner | professional
  explanation: detailed | concise
  selection: ai_recommended
  update: only_after_explicit_user_request
  unattended: never_ask_style_questions
  record_copy: beginner_detailed
  record_copy_reason: Records may later be shown to a newcomer.
```

`audience: professional` and `explanation: concise` mean “use shorter,
professional wording and explain only when asked.” This is still respectful;
never imply that a user is less capable because the default is beginner-safe.

These two settings affect only the live conversation. Every Granoflow record
(task title and description, Analysis, Plan, progress, Delivery, review,
milestone note, and durable memory) must remain `beginner_detailed`. The record
may be handed to a new teammate later, so never save shorthand merely because
the current user prefers concise display.

## Respectful adaptation

When a user says that the explanation is too much, acknowledge the signal and
continue the current task. Do not make them configure a form. Say briefly that
future messages can be shorter, then ask only in an interactive run whether
they want this project's style changed. Persist a change only after the user
explicitly asks for it. If they later ask “为什么这样做？”，give the full
scenario, consequence, and reason again without shaming them.

When the user asks for more grounded detail, update only this project's rules
through the App-owned context attachment write path, read the section back,
and report the saved result. Never write a global profile or another project's
rules.

## Unattended runs

Set `interaction_budget: 0`. Read the project style at the start, let the AI
select normal implementation details, and never interrupt to ask how much
detail the user wants. Style is not a blocker. Stop only for a real boundary
such as missing user-only input, a forbidden external action, scope change, or
subjective acceptance. The final report can still state what style was used.

## Workflow invariant

All workflows (task capture, Analysis, Plan, execution progress, errors,
Delivery, reviews, and milestone notices) use the same resolved style. A
workflow must not silently fall back to technical jargon merely because it is
running unattended or because an error occurred. The display style may be
professional and concise, but the saved Granoflow copy is always beginner
friendly and detailed.
