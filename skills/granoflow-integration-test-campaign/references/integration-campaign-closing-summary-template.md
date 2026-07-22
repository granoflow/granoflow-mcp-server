# Integration Campaign Closing Summary Template

Copy to a campaign attachment or `temp/integration-campaign-closing-<project>-r<n>.json`
(JSON) / paired Markdown. Delete guidance comments. Fill `plain.*` and
`markdown_body` for **non-programmers first**; put paths/commands only under
「给开发者看的细节」.

Machine JSON example (lint this file or an equivalent object):

```json
{
  "schema": "granoflow_integration_campaign_closing_summary_v1",
  "contract_loaded": true,
  "plain_language_loaded": true,
  "audience": "beginner",
  "locale": "zh-Hans",
  "outcome": "green",
  "rounds_completed": 1,
  "code_changed": false,
  "residuals": [],
  "acceptance_outcomes_loaded": true,
  "user_path_claim": "service_layers_only",
  "acceptance_outcomes": [
    {
      "id": "AO-domain-example",
      "statement": "模块协作后的真实数据结果已落盘/可读",
      "layer": "domain_io",
      "evidence_kind": "real_side_effect",
      "status": "closed",
      "case_ids": []
    }
  ],
  "plain": {
    "headline": "集成测试已经全部通过。",
    "what_we_checked": "按模块协作顺序检查了服务层真实读写（不是界面点击）：例如建库落盘、导入、列表过滤、打开到可读。",
    "result": "这些检查都通过了。",
    "what_changed_for_you": "应用对你来说没有变化；这次只整理了自动检查的顺序。",
    "leftovers": "没有未完成事项。",
    "next_step": "可以说「开始 E2E 战役」继续界面路径与截图检查。"
  },
  "change_report": {
    "schema": "granoflow_integration_campaign_change_report_v1",
    "status": "no_code_changes",
    "product_changes": [],
    "test_changes": [],
    "product_behavior_delta": "none",
    "why": "首轮编排后即全部通过",
    "failed_before": [],
    "passed_after_evidence": "orchestrated suite round 1 green"
  },
  "markdown_body": "见下方 Markdown 骨架（写入同一字段时保留全部必填标题）"
}
```

Omit vision/screenshot/window fields (E2E-only).

---

用户可见 Markdown 骨架（写入 `markdown_body`；标题文字不要改）：

```markdown
## 一句话结论

（用日常用语写结果。不要只写 phase/complete 之类内部词。）

## 这次查了什么

（用「建库→导入→列表数据→打开」描述模块协作；少用测试文件名。不要假装做过界面点击。）

## 结果如何

（通过 / 通过但还有遗留 / 因外部原因没跑完——说人话。）

## 对你有什么影响

（用户能感觉到的变化。若只改了测试脚本，写「对你没有影响，只是检查方式更合理」。
不要只贴 `src/...` 路径。）

### 若有过失败，用这三句说清楚

1. **当时哪里不对：** …
2. **我们怎么处理的：** …（产品改了 / 检查方式改了）
3. **现在为什么可以放心：** …

## 还剩什么没做完

（没有就写「没有未完成事项。」有遗留就写要你做什么。）

## 下一步你可以做什么

（给一句可直接回复的话，例如：可以说「开始 E2E 战役」。不要直接跳到「项目收尾」。）

## 给开发者看的细节

（命令、路径、Suite Plan 引用。）
```
