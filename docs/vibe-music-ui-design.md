# Vibe Music 像素终端音乐播放器 — 界面设计详细文档

> 本文档描述当前已实现的界面设计，包含所有 CSS 变量、布局参数、组件规格、交互逻辑和渲染细节。
> 最后更新：2026-05-23

---

## 1. 设计概述

Vibe Music 是一款赛博朋克风格的桌面音乐播放器，界面模拟"夜间运行的音频控制终端"。整体视觉语言为：暗色底色 + 青绿色荧光 + 像素字体 + 薄线框面板 + CRT 扫描线。

技术栈：Python + pywebview + Flask + HTML/CSS/JS + Canvas

### 核心关键词

- 复古未来主义（Retro-Futurism）
- 像素终端（Pixel Terminal）
- 赛博朋克（Cyberpunk）
- CRT 显示器质感
- 云端音乐播放器
- 跨平台（Ubuntu / Windows）

---

## 2. 色彩系统

### 2.1 CSS 变量定义

```css
:root {
  --bg:          #0a0f0d;    /* 页面主背景 */
  --bg-deep:     #050806;    /* 最深背景层，时钟面板、输入框底色 */
  --bg-card:     #0d1a12;    /* 面板卡片背景 */
  --ink:         #d7ffe8;    /* 主文字色，高对比度薄荷绿白 */
  --muted:       #6faa8a;    /* 次要文字，元信息、表格内容 */
  --dim:         #2e4a39;    /* 暗淡文字，占位符、表头、标签 */
  --green:       #7dffb2;    /* 主荧光色，激活态、进度条、时钟 */
  --green-glow:  rgba(125,255,178,.4);  /* 绿色辉光，用于 shadow */
  --cyan:        #6fd6ff;    /* 青色，时间戳、弹幕高亮 */
  --amber:       #ffd36e;    /* 琥珀色，音量条、弹幕、提示 */
  --red:         #ff6f7f;    /* 红色，错误状态 */
  --line:        #1e3d2e;    /* 面板分隔线、网格背景线 */
  --line-active: #3c8f62;    /* 激活边框，按钮、进度条边框 */
  --line-soft:   rgba(125,255,178,.12);  /* 柔和分隔线 */
  --cell:        4px;        /* 基础网格单元 */
  --radius:      0px;        /* 全局圆角，全部直角 */
}
```

### 2.2 色彩使用规则

| 场景 | 使用颜色 | 说明 |
|------|---------|------|
| 时钟数字 | `#7dffb2` | Canvas 渲染，带辉光 |
| 播放状态激活 | `--green` 背景 + `--bg-deep` 文字 | 反色高亮 |
| 进度条填充 | `--green` 渐变 | 从实色到半透明 |
| 音量条填充 | `--amber` 渐变 | 从实色到半透明 |
| 歌词文字 | `--green` | 带绿色辉光 |
| 弹幕文字 | `--amber` / `--cyan` | 70% 琥珀，30% 青色 |
| 时间戳 | `--cyan` | Press Start 2P 字体 |
| 错误提示 | `--red` | Toast 边框 |
| 面板标题圆点 | `--green` | 带脉冲呼吸动画 |

---

## 3. 字体系统

### 3.1 字体加载

通过 Google Fonts 加载两个字体：

```html
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Pixelify+Sans&display=swap" rel="stylesheet">
```

### 3.2 字体使用规则

| 用途 | 字体 | 大小 | 说明 |
|------|------|------|------|
| 全局文字 | `"Pixelify Sans", "LXGW WenKai Mono", "Noto Sans Mono CJK SC", "Microsoft YaHei UI", monospace` | 10-11px | 主 UI 文字 |
| 时钟数字 | 手写 `5x7` 像素矩阵 | 动态计算 | 由独立方块拼出数字，参考老式点阵电子钟 |
| 日期 | `"Press Start 2P", monospace` | 10px | 英文缩写格式 |
| 歌曲标题 | `"Pixelify Sans", monospace` | 20px | 带微弱绿色辉光 |
| 状态标签 | `"Press Start 2P", monospace` | 8-9px | STATUS / MODE 等 |
| 进度时间 | `"Press Start 2P", monospace` | 9px | 绿色带辉光 |
| 音量标签 | `"Press Start 2P", monospace` | 8px | VOL / 数值 |
| 底部状态栏 | `"Press Start 2P", monospace` | 9px | 暗淡色 |

### 3.3 渲染设置

```css
html, body {
  image-rendering: pixelated;
  -webkit-font-smoothing: none;
}
```

Canvas 渲染时钟时：
```js
ctx.imageSmoothingEnabled = false;
```

---

## 4. 全局效果

### 4.1 CRT 扫描线

通过 `body::before` 伪元素实现，覆盖全页面：

```css
body::before {
  position: fixed; inset: 0;
  pointer-events: none; z-index: 100;
  background: repeating-linear-gradient(
    to bottom,
    transparent 0px,
    transparent 2px,
    rgba(0,0,0,.12) 2px,
    rgba(0,0,0,.12) 4px
  );
}
```

- 每 4px 一个循环（2px 透明 + 2px 半透明黑）
- 透明度 12%，不影响阅读
- z-index: 100，覆盖所有内容但不可交互

### 4.2 暗角与氛围光

通过 `body::after` 伪元素实现：

```css
body::after {
  position: fixed; inset: 0;
  pointer-events: none; z-index: 99;
  background:
    radial-gradient(ellipse 120% 80% at 50% 50%, rgba(125,255,178,.015) 0%, transparent 70%),
    radial-gradient(ellipse at 50% 100%, rgba(0,0,0,.5) 0%, transparent 50%);
}
```

- 中心微弱绿色光晕（1.5% 透明度）
- 底部暗角渐变（50% 透明度黑色）

---

## 5. 布局架构

### 5.1 整体结构

```
┌─────────────────────────────────────────────────────────────────────┐
│ App Bar (36px)                                                       │
├───────────────┬─────────────────────────────┬───────────────────────┤
│ 像素时钟       │  当前播放                    │  专辑封面             │
│ (420px)       │  (1fr)                      │  (220px)             │
│               │                             │                      │
│               │                             │                      │
├───────────────┼──────────────────┬──────────┴──────────────────────┤
│ 播放队列       │  可视化           │  云端助手                      │
│ (1.05fr)      │  (0.9fr)         │  (1fr)                        │
│               │                  │                                │
├───────────────┴──────────────────┴────────────────────────────────┤
│ Status Bar (26px)                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 窗口网格

```css
.window {
  grid-template-rows: 36px 280px minmax(0, 1fr) 26px;
}
```

- 第 1 行：顶部栏 36px
- 第 2 行：Hero 区域 280px（时钟 + 播放 + 专辑）
- 第 3 行：工作区自适应填充
- 第 4 行：状态栏 26px

### 5.3 Hero 区域网格

```css
.hero {
  grid-template-columns: 420px minmax(0, 1fr) 220px;
  gap: 1px;
  background: var(--line);  /* 1px 间距用背景色填充，形成分隔线 */
}
```

- 左栏：像素时钟 420px
- 中栏：当前播放，自适应
- 右栏：专辑封面 220px

### 5.4 工作区网格

```css
.workspace {
  grid-template-columns: 1.05fr 0.9fr 1fr;
  gap: 1px;
  background: var(--line);
}
```

- 左栏：播放队列（略宽）
- 中栏：可视化（略窄）
- 右栏：云端助手

### 5.5 响应式

```css
@media (max-width: 1100px) {
  .hero { grid-template-columns: 340px minmax(0, 1fr) 200px; }
  .workspace { grid-template-columns: 1fr 1fr; }
  .agent-panel { grid-column: 1 / -1; }
}
```

---

## 6. 组件详细规格

### 6.1 顶部栏（App Bar）

**尺寸**：高度 36px，内边距 0 14px

**左侧品牌区**：
- 像素 Logo：14×14px，八边形裁切（`clip-path: polygon`），绿色填充
- Logo 辉光：`box-shadow: 0 0 8px green-glow, ±2px 0 0 green, 0 ±2px 0 green`（十字辉光）
- Logo 呼吸动画：3s ease-in-out，opacity 1 → 0.7 → 1
- 品牌名：`氛围音乐`，11px Press Start 2P，绿色，带 6px 辉光

**右侧操作区**：
- 频道标签：`云端`（默认激活）、`跨平台`
  - 高度 22px，内边距 0 8px
  - 1px `--line-active` 边框
  - 激活态：绿色背景 + 深色文字
  - 过渡：0.15s steps(3)
- 窗口按钮：最小化 / 最大化 / 关闭
  - 14×14px，1px `--line` 边框
  - hover 时整块变绿
  - 图标用 CSS 像素方块绘制（非 Unicode）

### 6.2 像素时钟面板

**位置**：Hero 左栏，420px 宽

**背景**：`--bg-deep`（#050806），无边框、无阴影

**结构**：
```
┌─────────────────────────┐
│                         │
│      5x7 点阵时钟        │  ← flex:1，占满剩余高度
│      (block matrix)     │
│                         │
│    MAY 23, 2026         │  ← 日期，10px，dim 色
└─────────────────────────┘
```

**5x7 点阵渲染逻辑**：
- 不使用普通字体直接渲染时间数字。
- 每个数字由 `5 x 7` 方块矩阵拼出，字形参考老式像素数字。
- 颜色：`#7dffb2`，可保留轻微 CRT 氛围，但发光要克制。
- 冒号单独用方块绘制并闪烁。
- 字形重点：硬边、粗块、直角、少圆润、少模糊。
- 抗锯齿关闭：`imageSmoothingEnabled = false`

**日期格式**：英文月份缩写，如 `MAY 23, 2026`
- 字体：Press Start 2P，10px
- 颜色：`--dim`
- 字间距：3px
- 底部内边距：14px

### 6.3 当前播放面板

**位置**：Hero 中栏，自适应宽度

**背景**：`--bg-deep`

**结构（从上到下）**：

#### 6.3.1 系统信息行

```
STATUS: [就绪]  MODE: [列表循环]
```

- 高度：auto，内边距 8px 16px
- 底部 1px `--line` 分隔线
- 背景：`--bg-card`
- `STATUS:` / `MODE:` 标签：Press Start 2P，8px，`--dim` 色
- 状态值：`.key` 组件，9px，激活时绿色填充

#### 6.3.2 歌曲信息区

- 内边距：12px 16px
- `CURRENT_TRACK` 标签：Press Start 2P，7px，`--dim` 色
- 歌曲标题：Pixelify Sans，20px，`--ink` 色，单行省略号，带微弱绿色辉光
- 艺术家：Pixelify Sans，11px，`--muted` 色，单行省略号
- 歌词行：1px `--line-soft` 边框，`--bg-card` 背景，绿色文字带辉光，12px

#### 6.3.3 控制区

内边距：10px 16px，三行布局：

**第 1 行 — 播放按钮**：
- `|<` 上一首、`▶` 播放、`>|` 下一首、`↻` 模式
- 按钮尺寸：36×32px
- 1px `--line-active` 边框
- hover：边框变绿 + 10px 辉光 + 8% 绿色填充
- 激活态（播放中）：绿色背景 + 深色文字
- 点击：scale(0.92) 缩放反馈
- 过渡：0.12s steps(3)

**第 2 行 — 进度条**：
```
[00:00] [████████░░░░░░░░░░░] [03:26]
```
- 时间显示：Press Start 2P，9px，绿色带辉光，最小宽度 48px
- 进度条容器：flex:1
- 进度条：10px 高，1px `--line-active` 边框，`--bg-deep` 背景
- 分段刻度：每 8px 一条 1px 竖线（`rgba(30,61,46,.5)`），z-index:2
- 填充：绿色渐变（实色 → 80% 透明），8px 辉光
- 过渡：width 0.2s steps(8)
- 点击跳转：计算点击位置百分比

**第 3 行 — 音量条**：
```
VOL [████████░░░░░] 80
```
- `VOL` 标签：Press Start 2P，8px，`--dim` 色
- 音量条容器：flex:1，最大宽度 200px
- 音量条：8px 高，1px `--line-active` 边框
- 分段刻度：每 6px 一条 1px 竖线
- 填充：琥珀色渐变，6px 辉光
- 过渡：width 0.15s steps(6)
- 数值显示：Press Start 2P，9px，琥珀色带辉光

### 6.4 专辑封面面板

**位置**：Hero 右栏，220px 宽

**结构**：
- 面板头：28px，`● 专辑` + 缓存状态
- 像素封面区：1px `--line-active` 边框，45deg 斜条纹背景（16px 方格），居中占位文字
- 封面图片：`object-fit: cover`，`image-rendering: pixelated`
- 底部信息：歌词行样式，显示来源和同步数量

### 6.5 播放队列面板

**位置**：工作区左栏

**结构**：
- 面板头：28px，`● 播放队列` + 歌曲数量
- 工具栏：搜索输入框 + 搜索按钮
  - 输入框：24px 高，1px `--line-active` 边框，`--bg-deep` 背景
  - focus：边框变绿 + 6px 辉光
  - 占位符：`搜索歌曲...`，`--dim` 色
- 列表区域（局部滚动）：
  - 表头行：24px，8px 字号，`--dim` 色，大写，不可点击
  - 列：`#`(28px) | `标题`(1fr) | `来源`(48px) | `时长`(44px)
  - 数据行：28px 高，10px 字号，`--muted` 色
  - 活跃行：绿色文字 + 绿色背景(8%) + `▸` 左侧指示器
  - hover：6% 绿色背景
  - 行间分隔：1px `--line-soft`
  - 双击播放

### 6.6 可视化面板

**位置**：工作区中栏

**结构**：
- 面板头：28px，`● 可视化` + `实时`（闪烁动画）
- 标签切换：`频谱`（默认）/ `弹幕`
  - 24px 高，flex:1 等分
  - 激活态：绿色文字 + 绿色底部边框 + `--bg-card` 背景
- 频谱视图：
  - 48 根竖条，3px 宽，2px 最小高度
  - 绿色填充 + 4px 辉光
  - 高度根据播放状态动态计算（低频高、高频低 + 随机噪声）
  - 过渡：0.08s steps(3)
- 弹幕视图：
  - 弹幕从右向左漂移，7s 线性循环
  - 70% 琥珀色，30% 青色（带辉光）
  - 每 1.5s 生成一条（仅播放时）
  - 随机垂直位置（5%-85%）
  - 随机持续时间（5-8s）

### 6.7 云端助手面板

**位置**：工作区右栏

**结构**：
- 面板头：28px，`● 云端助手` + `已连接`
- 对话区域（局部滚动）：
  - 用户消息：1px 绿色边框，右偏移 20px，`--ink` 色
  - 助手消息：1px 青色边框，左偏移 16px，`--muted` 色
  - 元信息：`我 HH:MM` / `助手 HH:MM`，Press Start 2P，8px，`--cyan` 色
  - 消息间距：6px
- 输入区：34px 高
  - 输入框：grid 1fr + 30px
  - 发送按钮：`>` 像素按钮
  - Enter 键发送

**支持的指令**：
- 歌曲名关键词 → 搜索并播放
- `播放` / `继续` → 恢复播放
- `暂停` / `停止` → 暂停
- `下一首` → 切换下一首
- `上一首` → 切换上一首

### 6.8 底部状态栏

**尺寸**：高度 26px，内边距 0 12px

**内容**：
- 左侧：`音频：默认输出 | 内存：XX.XG | CPU：XX%`
- 右侧：`v1.0.0-BETA | 桌面端就绪`

**样式**：
- 字体：Press Start 2P，9px
- 颜色：`--dim`
- 顶部 1px `--line` 分隔线
- 内存和 CPU 每 5 秒随机更新（模拟数据）

---

## 7. 通用组件规格

### 7.1 面板（.panel）

```css
.panel {
  min-width: 0; min-height: 0;
  background: var(--bg-card);
  overflow: hidden;
  position: relative;
}
```

### 7.2 面板头（.panel-head）

- 高度 28px
- 底部 1px `--line` 分隔线
- 背景 `--bg-deep`
- 左侧：绿色圆点（6×6px，6px 辉光，2s 脉冲呼吸）+ 标题
- 右侧：状态文字

### 7.3 标签/按键（.chip / .key / .tab）

- 高度 22px
- 1px `--line-active` 边框
- 内边距 0 8px
- 字号 9px
- hover：绿色边框 + 8px 辉光
- 激活态（.on）：绿色背景 + 深色文字
- 过渡：0.15s steps(3)

### 7.4 像素按钮（.pixel-btn）

- 尺寸 36×32px
- 1px `--line-active` 边框
- hover：绿色边框 + 10px 辉光 + 8% 绿色填充（::before 伪元素）
- 激活态：绿色背景 + 深色文字
- 点击：scale(0.92)
- 过渡：0.12s steps(3)

### 7.5 滚动区域（.scroll）

- 自定义滚动条：5px 宽
- 轨道：`--bg-deep`
- 滑块：`--line-active`
- Firefox：`scrollbar-width: thin`

### 7.6 Toast 提示

- 固定定位：top 50px，right 16px
- 背景 `--bg-card`，1px 绿色边框
- 绿色文字，Press Start 2P 字体，10px
- 12px 绿色辉光
- 动画：2.5s fadeInOut
  - 0%：透明 + 上移 8px
  - 15%：完全显示
  - 85%：保持
  - 100%：淡出

### 7.7 加载动画

- 绿色文字 + 10px 旋转边框方块
- 边框 1px `--line`，顶部边框 `--green`
- 0.8s 线性旋转

---

## 8. 动画系统

### 8.1 动画清单

| 动画名 | 周期 | 类型 | 用途 |
|--------|------|------|------|
| `logoPulse` | 3s | ease-in-out | Logo 呼吸，opacity 1→0.7→1 |
| `dotPulse` | 2s | ease-in-out | 面板头圆点呼吸，opacity 1→0.5→1 |
| `blink` | 1.1s | steps(2, end) | 冒号闪烁、实时标签闪烁 |
| `fly` | 7s | linear | 弹幕从右向左漂移 |
| `spin` | 0.8s | linear | 加载旋转 |
| `fadeInOut` | 2.5s | ease | Toast 淡入淡出 |

### 8.2 Glitch 抖动（Canvas 时钟）

- 触发概率：每帧 5%
- 偏移量：fontSize × 1.5% × 随机方向
- 持续帧数：5-15 帧
- 衰减：每帧 ×0.6

### 8.3 频谱动画

- 帧率：requestAnimationFrame（~60fps）
- 高度计算：base(8px) + low频(40px) + mid频(20px) + high频(10px) + noise(12px)
- 未播放时：base(2px) + noise(2px)，opacity 0.3
- 过渡：0.08s steps(3)

---

## 9. 交互逻辑

### 9.1 播放控制

| 操作 | 触发 | 行为 |
|------|------|------|
| 播放/暂停 | 点击 ▶ 按钮 | 切换播放状态，更新按钮文字（▶/||）和状态标签 |
| 上一首 | 点击 \|< 按钮 | 播放队列上一首，单曲循环时不变 |
| 下一首 | 点击 >\| 按钮 | 播放队列下一首，单曲循环时不变 |
| 播放模式 | 点击 ↻ 按钮 | 循环切换：列表循环→单曲循环→随机播放 |
| 进度跳转 | 点击进度条 | 计算点击位置百分比，跳转到对应时间 |
| 音量调节 | 点击音量条 | 计算点击位置百分比，设置音量 |

### 9.2 搜索与播放

1. 在搜索框输入关键词 → 点击搜索按钮或 Enter
2. 调用 `/api/search` 接口搜索歌曲
3. 结果填充到播放队列
4. 自动播放第一首
5. 同时在云端助手中显示搜索结果

### 9.3 队列管理

- 双击队列中的歌曲 → 播放该歌曲
- 当前播放歌曲高亮显示（绿色文字 + 绿色背景 + ▸ 指示器）
- 歌曲结束后根据播放模式自动切换

### 9.4 云端助手

- 输入文字 → 点击发送或 Enter
- 支持自然语言指令（播放/暂停/下一首/上一首）
- 支持歌曲搜索（其他文字当作搜索关键词）
- 消息区分用户/助手，不同边框颜色

---

## 10. API 接口

| 接口 | 方法 | 参数 | 返回 |
|------|------|------|------|
| `/api/search` | POST | `{keyword, limit}` | `{code, songs: [{id, title, artist, album, duration, source}]}` |
| `/api/song_url` | POST | `{id}` | `{code, url}` |
| `/api/lyric` | POST | `{id}` | `{code, lyric}` |
| `/api/top_songs` | GET | - | `{code, songs}` |

Flask 服务端口：52400
NCM API 端口：52401

---

## 11. 窗口尺寸规格

| 项目 | 值 |
|------|---|
| 最小窗口 | 1024 × 680 |
| 窗口内边距 | 6px |
| 窗口边框 | 1px `--line` |
| 窗口阴影 | 0 0 0 1px rgba(125,255,178,.04), 0 0 40px rgba(0,0,0,.6) |

---

## 12. 界面语言规则

- 主界面文字：**中文**
- 技术标签（STATUS / MODE / VOL / CURRENT_TRACK）：**英文大写**
- 日期格式：**英文月份缩写**（MAY 23, 2026）
- 状态文字：**中文**（就绪 / 播放中 / 已暂停 / 列表循环 / 单曲循环 / 随机播放）
- 面板标题：**中文**（专辑 / 播放队列 / 可视化 / 云端助手）
- 底部状态栏：**中文**（音频：默认输出 | 内存：XX | CPU：XX）
