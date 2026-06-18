---
name: server-manager
description: |
  用于通过SSH管理远程Linux服务器。

  适用于：
  - 查看训练状态
  - 查看GPU占用
  - 启动或停止项目
  - 查看日志
  - 执行Linux命令

---

# Server Manager Skill

当用户要求：

- 查看服务器状态
- SSH连接服务器
- 查看GPU
- 查看训练
- 查看tmux
- 启动训练
- 重启项目
- 查看日志

时，使用此skill。

# Workflow

1. 使用 python scripts/ssh_manager.py "<command>"
2. 获取输出
3. 总结结果给用户

# Common Commands

## 查看GPU

```bash
nvidia-smi
```

## 查看tmux

```
tmux ls
```

## 查看训练日志

```
tail -n 50 train.log
```

## 查看进程

```
ps aux | grep python
```