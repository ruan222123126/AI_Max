# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI_Max is a new project directory. The repository currently contains minimal infrastructure.

## Task Management Workflow

All tasks are managed in the `task/` directory with the following workflow:

1. **Task Creation**: Each new task is documented as a markdown file in the `task/` directory
2. **Task Execution**: Work on the task according to the requirements in the task file
3. **Completion Report**: When a task is completed, write a completion report in the `finish/` directory with the same filename
4. **Archival**: Move the completed task file from `task/` to the `OK/` directory

Directory structure:
- `task/` - Contains active/pending task files
- `finish/` - Contains completion reports for finished tasks
- `OK/` - Archive for completed task files

## Desktop Notifications

This project has a desktop notification system configured for task completion updates. Use the provided script to send notifications:

```bash
# Success notification (green)
/media/ruan/Files/AI_Max/.claude/task-notify.sh "✅ 任务完成" "具体任务描述" "normal"

# Warning notification (yellow)
/media/ruan/Files/AI_Max/.claude/task-notify.sh "⚠️ 注意" "警告信息" "normal"

# Error notification (red)
/media/ruan/Files/AI_Max/.claude/task-notify.sh "❌ 错误" "错误信息" "critical"
```

The script uses `notify-send` and falls back to stdout if unavailable. Supported emoji icons:
- ✅ Success/Completion
- ⚠️ Warning/Attention
- ❌ Error/Failure
- ℹ️ Information/Tips
- 🚀 New Feature/Release
- 🐛 Bug Fix
- 🔧 Configuration/Tools
- 📝 Documentation/Comments

See `.claude/TASK_COMPLETE.md` for additional usage examples.
