# 宏键盘项目复查报告
复查日期：2026-05-26

## 总体评价

项目整体质量很高，文件完整，文档结构清晰，中英双语一致性好。12 天课程内容循序渐进，技术覆盖全面。主要问题集中在评分体系的一致性上：README.md 和 assignments/rubric.md 使用 115 分制（含 15 分 Demo 网站），而 overview.md 和 curriculum/grading-rubric.md 仍使用 100 分制。此外，Day 03 代码中有一处注释符号错误需要修正。

---

## 检查结果

### 1. 文件完整性

所有必需文件均存在，无缺失：

- [x] README.md
- [x] resources/search-results.md
- [x] curriculum/overview.md
- [x] curriculum/prerequisites.md
- [x] curriculum/assignments.md
- [x] curriculum/grading-rubric.md
- [x] curriculum/day-01.md ~ day-12.md（12 个文件全部齐全）
- [x] hardware/BOM.md
- [x] hardware/wiring-guide.md
- [x] hardware/assembly-steps.md
- [x] hardware/troubleshooting.md
- [x] software/requirements.txt
- [x] software/config.template.yaml
- [x] software/src/main.py
- [x] software/src/keymatrix.py
- [x] software/src/oled_display.py
- [x] software/src/rgb_led.py
- [x] software/src/encoder.py
- [x] software/src/usb_hid.py
- [x] software/src/utils.py
- [x] software/tests/test_basic.py
- [x] assignments/week-1-checkin.md
- [x] assignments/week-2-checkin.md
- [x] assignments/final-presentation.md
- [x] assignments/rubric.md

文件完整性：**全部通过**（26 个文件均已存在）。

---

### 2. 内容质量

#### README.md
- [x] 包含 B 站视频链接（8 个视频 + 5 位推荐 UP 主）
- [x] BOM 总预算 ~146.4 元，远低于 500 元上限
- [x] 中英双语格式完整
- [x] 包含课程安排、评分标准、项目结构、FAQ 等完整信息

#### 每日课程 day-XX.md
- [x] 全部 12 天均有"为什么学这个"（Why Learn This）部分
- [x] 全部 12 天均有时间安排表（Schedule）
- [x] 全部 12 天均有作业（Homework）部分
- [x] 全部 12 天均有明日预告（Tomorrow's Preview）
- [x] 全部 12 天均有参考资源（References）部分

#### BOM.md
- [x] 价格合理（核心器件 61.4 元 + 被动元件约 1 元 + PCB 5 元 + 连接结构 75 元 = ~146 元）
- [x] 包含详细采购建议（分嘉立创商城、嘉立创 PCB、淘宝三个渠道）
- [x] 包含采购时间线（开课前/Day 6 后/Day 7 后）
- [x] 包含替代方案（ATmega32U4/RP2040/Kailh 等）
- [ ] **问题**：被动元件小计标示为 ~1.0 元，但实际按包采购（10 个起卖，约 0.2 元/包）的成本约为 2 元，虽然影响不大但标注不够准确

#### 代码文件中文注释
- [x] software/src/main.py：模块 docstring、函数 docstring、关键注释均有中英双语
- [x] software/src/keymatrix.py：同上
- [x] software/src/oled_display.py：同上
- [x] software/src/rgb_led.py：同上
- [x] software/src/encoder.py：同上
- [x] software/src/usb_hid.py：同上
- [x] software/src/utils.py：同上
- [x] software/tests/test_basic.py：同上
- [x] 课程文件中的 C 代码示例（day-01 ~ day-11）：均有中文注释

#### Demo 网站要求覆盖情况
- [x] final-presentation.md：第 17-57 行，详细要求和评分标准（15 分）
- [x] rubric.md：第 57-65 行，"四、Demo 网站 (15 分)"完整评分细则
- [x] day-12.md：第 104-141 行，"任务 12.3: 创建项目展示网站"包含完整步骤和内容清单
- [x] README.md：第 143 行，评分表中明确列出 "Demo 网站 Project Demo Website | 15 分"

Demo 网站要求：**在四个关键文件中均已包含**。

---

### 3. 一致性检查

#### 课程天数
- [x] README.md：12 天（课程表 Day 01 ~ Day 12）
- [x] overview.md：12 天（结构图 Day 1-12）
- [x] 实际文件：day-01.md ~ day-12.md，共 12 个文件
- 课程天数：**全部一致**（均为 12 天）

#### 评分标准一致性
- [ ] **重大不一致**：评分体系在不同文件中存在冲突

| 文件 | 总分 | 是否含 Demo 网站 | 状态 |
|------|------|------------------|------|
| README.md | 115 分 | 是（15 分） | 新版 |
| assignments/rubric.md | 115 分 | 是（15 分） | 新版 |
| curriculum/grading-rubric.md | 100 分 | 否 | **旧版，需更新** |
| curriculum/overview.md | 100%（对应 100 分） | 否 | **旧版，需更新** |
| CLAUDE.md（父目录模板） | 100% | 否 | 模板，可保留 |

具体差异：
- overview.md 第 115-123 行的评估体系表格使用 100% 权重，缺少 Demo 网站项
- curriculum/grading-rubric.md 总分表（第 5-12 行）为 100 分，缺少 Demo 网网站维度
- README.md 和 assignments/rubric.md 已统一为 115 分制（含 15 分 Demo 网站）

#### 硬件清单与接线指南一致性
- [x] BOM.md 中的 STM32F103C8T6、SSD1306 OLED、WS2812B、EC11、1N4148、Type-C 接口 -- 与 wiring-guide.md 中的接线描述完全一致
- [x] 引脚分配一致：PA0-PA3 (ROW)、PA4-PA7 (COL)、PA8 (WS2812B DIN)、PB0/PB1 (ENC A/B)、PB5 (ENC SW)、PB6/PB7 (I2C SCL/SDA)、PA11/PA12 (USB D-/D+)
- [x] BOM 中列出的 220 ohm、330 ohm、4.7k ohm、10k ohm 电阻 -- 与 wiring-guide.md 中各处描述匹配
- [x] AMS1117-3.3 LDO -- 与 wiring-guide.md 电源系统部分一致
- 硬件清单与接线指南：**完全一致**

#### 课程安排与软件模块对应关系
- [x] Day 2（矩阵扫描）--> keymatrix.py（Python 模拟）+ day-02.md 中的 C 代码
- [x] Day 3（I2C / OLED）--> oled_display.py（Python 模拟）+ day-03.md 中的 C 代码
- [x] Day 4（RGB LED）--> rgb_led.py（Python 模拟）+ day-04.md 中的 C 代码
- [x] Day 9（USB HID）--> usb_hid.py（Python 模拟）+ day-09.md 中的 HID 协议讲解
- [x] encoder.py 对应旋钮编码器内容（Day 11 集成调试部分）
- [x] main.py 作为工具入口，整合所有模块
- [x] test_basic.py 测试所有模块
- 课程与代码模块对应：**完全一致**

---

### 4. B 站视频链接检查

#### README.md 中的 B 站链接
- [x] 8 个精选视频（PCB 设计 3 个 + QMK 固件 5 个），全部含 BV 号链接
- [x] 5 位推荐 UP 主含主页链接
- [x] 4 个 GitHub 开源项目链接
- [x] 6 个官方文档链接

#### search-results.md 中的完整视频列表
- [x] PCB 设计系列教程：9 个视频（含 BV 号和播放量/时长）
- [x] QMK 固件开发系列教程：13 个视频
- [x] 7 位推荐 UP 主（含主页链接）
- [x] 13 个 GitHub 开源项目
- [x] 完整的学习教程资源（矩阵扫描、PCB 设计、RGB 焊接、QMK 路径等）
- [x] 采购参考（主控方案 4 种 + 核心元器件清单 + 采购渠道 4 个）
- [x] 学习路线图（5 个阶段）

#### day-XX.md 中的参考视频链接
- [x] day-01.md：4 个参考链接（QMK 矩阵文档 + B 站搜索建议 + 浚达良视频）
- [x] day-02.md：4 个参考链接（QMK 文档 + matrix.c + B 站搜索 + HiryKun 视频）
- [x] day-03.md：4 个参考链接（SSD1306 数据手册 + QMK OLED 文档 + B 站搜索）
- [x] day-04.md：4 个参考链接（YK-Yan 焊接视频 + HiryKun RGB 视频 + B 站搜索 + 数据手册）
- [x] day-05.md：4 个参考链接（嘉立创 EDA + oshwhub + B 站搜索 + 浚达良视频）
- [x] day-06.md：4 个参考链接（苏达视频 + 丈二先生视频 + 嘉立创文档 + Sofle 项目）
- [x] day-07.md：4 个参考链接（嘉立创打样教程 + 苏达视频 + JLCPCB + QMK 文档）
- [x] day-08.md：5 个参考链接（QMK 文档 + 配置器 + HiryKun ARM 移植 + 浮靈君环境搭建 + 浚达良工具介绍）
- [x] day-09.md：6 个参考链接（QMK Toolbox + 浚达良三部曲 3 集 + USB HID 规范 + 书籍）
- [x] day-10.md：4 个参考链接（YK-Yan RGB 焊接 + 丈二先生焊接固件 + B 站搜索 2 条）
- [x] day-11.md：4 个参考链接（QMK RGB/OLED/编码器文档 + HiryKun EEPROM 视频）
- [x] day-12.md：4 个参考链接（双旋钮展示视频 + 2KEY 宏键盘视频 + QMK 社区 + oshwhub）

B 站视频链接：**覆盖完整**，README、search-results.md、每日课程三个层级均有充分的视频资源。

---

### 5. 格式检查

#### "最后更新"日期
- [x] README.md：*最后更新 | Last updated: 2026-05-26*
- [x] resources/search-results.md：搜索日期：2026-05-26（首行）
- [x] curriculum/overview.md：*最后更新 | Last updated: 2026-05-26*
- [x] curriculum/prerequisites.md：*最后更新 | Last updated: 2026-05-26*
- [x] curriculum/assignments.md：*最后更新 | Last updated: 2026-05-26*
- [x] curriculum/grading-rubric.md：*最后更新 | Last updated: 2026-05-26*
- [x] curriculum/day-01.md ~ day-12.md：全部为 *最后更新 | Last updated: 2026-05-26*
- [x] hardware/BOM.md：*最后更新 | Last updated: 2026-05-26*
- [x] hardware/wiring-guide.md：*最后更新 | Last updated: 2026-05-26*
- [x] hardware/assembly-steps.md：*最后更新 | Last updated: 2026-05-26*
- [x] hardware/troubleshooting.md：*最后更新 | Last updated: 2026-05-26*
- [x] software/requirements.txt：# 最后更新 | Last updated: 2026-05-26
- [x] software/config.template.yaml：# 最后更新 | Last updated: 2026-05-26
- [x] software/src/*.py（7 个文件）：全部为 # 最后更新 | Last updated: 2026-05-26
- [x] software/tests/test_basic.py：# 最后更新 | Last updated: 2026-05-26
- [x] assignments/week-1-checkin.md：*最后更新 | Last updated: 2026-05-26*
- [x] assignments/week-2-checkin.md：*最后更新 | Last updated: 2026-05-26*
- [x] assignments/final-presentation.md：*最后更新 | Last updated: 2026-05-26*
- [x] assignments/rubric.md：*最后更新 | Last updated: 2026-05-26*

日期检查：**全部为 2026-05-26，完全一致**。

#### 中英双语检查
- [x] 所有 .md 文件：标题、表头、正文均采用"中文 | English"双语格式
- [x] 所有 Python 代码文件：docstring 采用中英双语，注释采用中文 + 英文对照
- [x] 课程中的 C 代码示例：注释采用中文 + 英文对照
- [x] YAML 配置文件：键名用英文，注释用中文 + 英文

中英双语：**全部通过**。

#### 表格格式检查
- [x] 所有 Markdown 表格格式正确，表头分隔符（|---|---|）齐全
- [x] 无表格列数不匹配的情况
- [x] 无表格对齐错误

表格格式：**全部正确**。

---

## 需要修复的问题

### 问题 1（严重）：评分体系不一致 -- overview.md

**文件**：`curriculum/overview.md`
**行号**：第 115-123 行
**问题**：评估体系表格使用百分比权重（总计 100%），未包含 Demo 网站项。与 README.md 和 assignments/rubric.md 的 115 分制不一致。

当前内容：
```
| 每日实验完成度 | 20% | 每天 17:00 |
| Week 1 进度汇报 | 10% | Day 4 结束 |
| Week 2 进度汇报 | 10% | Day 8 结束 |
| PCB 设计文件 | 15% | Day 7 结束 |
| 固件源代码 | 15% | Day 9 结束 |
| 最终项目展示 | 20% | Day 12 |
| 文档与代码质量 | 10% | Day 12 |
```

### 问题 2（严重）：评分体系不一致 -- grading-rubric.md

**文件**：`curriculum/grading-rubric.md`
**行号**：第 5-12 行（总分表）
**问题**：总分表为 100 分，缺少 Demo 网站维度。与 README.md 和 assignments/rubric.md 的 115 分制不一致。

当前内容：
```
| 技术实现 Technical Implementation | 40% | 40 |
| 文档质量 Documentation Quality | 20% | 20 |
| 演示展示 Final Presentation | 20% | 20 |
| 进度汇报 Check-in Reports | 10% | 10 |
| 团队协作 & 学习态度 | 10% | 10 |
| **总计 Total** | **100%** | **100** |
```

### 问题 3（轻微）：代码注释符号错误

**文件**：`curriculum/day-03.md`
**行号**：第 215 行
**问题**：C 代码中使用了 `|` 而非 `//` 作为注释符号。

当前内容：
```c
    oled_send_command(0x81);  | 设置对比度 | Set contrast
```

正确内容应为：
```c
    oled_send_command(0x81);  // 设置对比度 | Set contrast
```

### 问题 4（轻微）：BOM 被动元件价格标注不够精确

**文件**：`hardware/BOM.md`
**行号**：第 47 行
**问题**：被动元件小计标示为 ~1.0 元，但逐项加总为 0.64 元（0.04+0.02+0.04+0.02+0.04+0.08+0.10+0.10+0.30+0.30）。虽然注释说明"10 个起卖，约 0.2 元/包"是正确的，但小计数字与逐项总和不完全匹配。建议统一为"约 2 元（含最低采购量）"。

---

## 修复建议

### 建议 1：统一评分体系为 115 分制

将 `curriculum/overview.md` 第 115-123 行的评估体系表格替换为与 README.md 一致的 115 分制：

```markdown
| 评估项 Assessment Item | 满分 Points | 截止时间 Deadline |
|---|---|---|
| 技术实现 | 40 分 | Day 12 |
| 文档质量 | 20 分 | Day 12 |
| 演示展示 | 20 分 | Day 12 |
| Demo 网站 | 15 分 | Day 12 |
| 进度汇报 | 10 分 | Day 4 / Day 8 |
| 团队协作 | 10 分 | Day 12 |
| **总分** | **115 分** | |
```

### 建议 2：更新 grading-rubric.md 总分表

将 `curriculum/grading-rubric.md` 第 5-12 行的总分表替换为：

```markdown
| 维度 Dimension | 权重 Weight | 满分 Points |
|---|---|---|
| 技术实现 Technical Implementation | -- | 40 |
| 文档质量 Documentation Quality | -- | 20 |
| 演示展示 Final Presentation | -- | 20 |
| Demo 网站 Project Demo Website | -- | 15 |
| 进度汇报 Check-in Reports | -- | 10 |
| 团队协作 & 学习态度 | -- | 10 |
| **总计 Total** | | **115** |
```

并在文件中添加"四、Demo 网站 (15 分)"章节，内容参考 `assignments/rubric.md` 第 57-65 行。

### 建议 3：修复 day-03.md 注释符号

将 `curriculum/day-03.md` 第 215 行：
```c
    oled_send_command(0x81);  | 设置对比度 | Set contrast
```
修改为：
```c
    oled_send_command(0x81);  // 设置对比度 | Set contrast
```

### 建议 4：修正 BOM 被动元件小计

将 `hardware/BOM.md` 第 47 行的小计从 `~1.0` 修改为 `~2.0`，并在备注中补充："按最低采购量（10 个/包，约 0.2 元/包）计算"。

---

## 复查总结

| 检查项 | 结果 |
|--------|------|
| 文件完整性 | 全部通过（26 个文件齐全） |
| 内容质量 | 通过（1 个代码注释符号错误 + 1 个 BOM 小计标注问题） |
| 一致性 | 需修复（评分体系在 2 个文件中不一致） |
| B 站视频链接 | 全部通过（README + search-results + 全部 12 天课程均有） |
| 格式 | 全部通过（日期、双语、表格均正确） |

**需要修复的问题：4 个（2 个严重 + 2 个轻微）**

---

*本报告由 Claude Code 自动生成*
*Report generated by Claude Code*
*2026-05-26*
