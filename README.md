# A股交易日历

数据由 GitHub Actions 每个交易日北京时间 08:15 自动采集并提交到 `data/processed/`。
前端由 GitHub Pages 托管，读取这些 JSON 渲染。

## 手动触发
Actions → daily-update → Run workflow

## 定时
- GitHub 原生 schedule：`15 8 * * 1-5` + `Asia/Shanghai`（可能延迟）
- cron-job.org：每个工作日 UTC 00:15 调用 workflow_dispatch（精确定时）

## 数据口径
- 回购到期量由历史操作 + 期限推断，未来 14 天只展示到期量
- 前 5 名净持仓采用口径 A（前 5 多头席位各自净持仓求和）
- ETF 净申购金额 = Δ份额 × 成交均价，四只分别计算不加总
- 情绪评分四维度等权，去掉北向因子，5 档映射
- 中美 5 年期利率为日频收盘值，不是 08:15 时刻值# stock-calendar
