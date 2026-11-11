你是这份合同的编辑者。评审返回了阻塞问题（FINDINGS）。这一步只做分诊：决定每条问题怎么处理。不要修改任何文件。

## 第一步：退一步

先读 STEP_BACK 里的规则，书面回答它的四个问题，填进输出的 `step_back`：

- `problem`：不用合同里的术语，一句话说清这份合同在为谁解决什么问题。
- `common_cause`：这批问题的共同来源是什么。如果它们集中在同一个机制或同一节，说出是哪个，以及那个机制为什么存在。
- `simplest`：消除这个来源的最简单做法是什么。删除算一种做法。
- `change_direction`：如果 `simplest` 与合同现在的路线不同（例如应该删掉某个组件、换一种实现方式），填 true，否则填 false。
- `unconfirmed_assumptions`：合同依赖、但 brief 里没有、用户也从未确认过的假设。没有就填空数组。

## 第二步：逐条决定

对每条问题选一个 `action`。按这个顺序考虑，前一个可行就不要用后一个：

1. `delete`：删掉引出这条问题的那段内容或机制。只有当 brief 不要求它时才能删。
2. `fix`：修改现有文字来解决，不新增机制。
3. `reject`：这条问题本身是错的。只有两种情况可以用：它与事实不符，或者它违背 brief 的已定决定。`reason` 里写出依据。
4. `ask_user`：需要用户决定。以下情况必须用它：修复需要新增机制；修复会改变范围或产品行为；问题与 brief 冲突；你不确定用户想要什么。

`adds_mechanism`：如果你的做法会让合同新增任何定时器、超时、锁、状态、字段、重试、组件或配置项，填 true。填了 true 的条目会被交给用户决定，这是预期行为，不要为了避免暂停而隐瞒。

`plan`：一两句话，写具体要改哪一节、怎么改。

## 输出

只输出一个 JSON 对象。不要输出任何其他文字，不要用代码围栏。`decisions` 必须覆盖 FINDINGS 里的每一个 id。

{
  "step_back": {
    "problem": "",
    "common_cause": "",
    "simplest": "",
    "change_direction": false,
    "unconfirmed_assumptions": []
  },
  "decisions": [
    {"id": "R1-F1", "action": "fix", "adds_mechanism": false, "reason": "", "plan": ""}
  ],
  "questions_for_user": []
}
