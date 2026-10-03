# Synthetic mock case


## Raw user input

```text
我的项目简历上现在写的是：

“主导开发 AI-native Minecraft 英语教育平台，
设计多 Agent 架构并完成 Runtime、Plugin、
ASR/TTS 与云端部署。”

感觉挺强的。

但实际上我主要是产品负责人。

课程、Teacher、流程、功能定义、团队协调这些是我负责；

代码很多是实习生和 Agent 写的，
我会 review，
也参与一些集成调试。

这句话能不能继续这么写？
```

## Known context

```yaml
user_role:
  - product_owner
  - project_lead

user_responsibilities:
  - product_definition
  - curriculum_structure
  - teacher_behavior
  - feature_prioritization
  - team_coordination
  - integration
  - acceptance

other_contributors:
  - runtime_implementation
  - minecraft_plugin
  - deployment
  - map_implementation

ai_coding_tools:
  used_by_multiple_contributors
```

Available evidence:

```text
PRD
course docs
Teacher design docs
project plans
QA documents
Git repo
handoff documents
```

Important boundary:

```text
Git / repo existence does not prove the user personally implemented all major components.
```

