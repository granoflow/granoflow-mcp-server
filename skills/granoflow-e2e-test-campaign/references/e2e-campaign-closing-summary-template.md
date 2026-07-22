# E2E Campaign Closing Summary Template

Copy to a campaign attachment or `temp/e2e-campaign-closing-<project>-r<n>.json`.
Fill `plain.*` and `markdown_body` for **non-programmers first**; embed or
reference the evidence pack.

Machine JSON example:

```json
{
  "schema": "granoflow_e2e_campaign_closing_summary_v1",
  "contract_loaded": true,
  "plain_language_loaded": true,
  "audience": "beginner",
  "locale": "zh-Hans",
  "outcome": "green",
  "rounds_completed": 1,
  "code_changed": false,
  "screenshot_capability": "available",
  "window_capability": "available",
  "vision_result": "passed",
  "residuals": [],
  "_comment_manual_skip": "If a journey was deferred_manual, use outcome green_with_residuals and residuals like {\"code\":\"e2e_campaign_manual_test_required\",\"feature\":\"桌面托盘最近书籍\",\"detail\":\"...\"}; leftovers must name that feature and ask for 手工测试.",
  "plain": {
    "headline": "界面端到端检查已经全部通过。",
    "what_we_checked": "像真人一样打开应用、完成主流程里的点击和输入。",
    "result": "这些界面步骤都通过了。",
    "what_changed_for_you": "应用对你来说没有变化；这次只确认了界面流程。",
    "leftovers": "没有未完成事项。",
    "next_step": "请先对下方「原型对照」做最终验收；全部认可后再说「项目收尾」。",
    "screenshots_note": "关键步骤截图保存在项目的临时文件夹里，并已在对话中展示给你看过。"
  },
  "evidence_pack": {
    "schema": "granoflow_e2e_evidence_pack_v1",
    "screenshot_capability": "available",
    "window_capability": "available",
    "checkpoints": ["home_loaded"],
    "screenshots": [
      {
        "step_id": "home_loaded",
        "path": "temp/e2e-campaign/1/screenshots/home_loaded.png",
        "shown_to_user": true,
        "capture_surface": "os_window"
      }
    ],
    "prototype_task_reviews": {
      "schema": "granoflow_e2e_prototype_task_reviews_v1",
      "inventory_loaded": true,
      "required_task_ids": [],
      "ai_loop_status": "not_applicable",
      "user_final_acceptance": false,
      "reviews": []
    }
  },
  "markdown_body": "见下方 Markdown 骨架"
}
```

---

用户可见 Markdown 骨架（写入 `markdown_body`）：

```markdown
## 一句话结论

（日常用语写结果。）

## 这次查了什么

（打开应用 → 点哪里 → 看到什么。）

## 结果如何

（通过 / 通过但有遗留 / 外部原因没跑完。）

## 对你有什么影响

（用户能感觉到的变化；若只改了测试，写对你没有影响。）

## 关键步骤截图

（说明已在对话展示；可列出步骤名称。不要只贴内部路径。）

## 原型对照

（对每个定稿任务级原型循环列出：1）可点击原型链接；2）对应实机截图；
3）AI 三项评估是否通过。有原型无截图是流程错误，必须补上。
横竖屏或桌面/手机形态差异不算保真度差异。
AI 未通过项不得在此要求用户收尾——应已自动建任务并进入下一轮战役。）

## 还剩什么没做完

（没有就写「没有未完成事项。」）

## 下一步你可以做什么

（AI 全绿后：请做原型对照最终验收。用户认可后才说「项目收尾」。）

## 给开发者看的细节

（可选：evidence pack、change report、命令。）
```

When `screenshot_capability: unavailable`, do **not** omit 「关键步骤截图」 to
claim a green close—the campaign **Must** fail closed as
`e2e_campaign_window_required`.
