# Synthetic mock case


## Raw user input

```text
现在手上两个 Offer，我挺纠结。

A 是深圳某大厂 AI 产品经理，
月薪 28k × 16，
团队成熟，
做 AI 搜索产品，
但我进去应该负责比较细的一个模块。

B 是香港一家 25 人的 AI startup，
月薪 HKD 35k × 12，
Title 是 AI Product Engineer。

Founder 说进去以后从产品到 Agent workflow 都可以做，
甚至直接跟客户。

我以后可能还是想创业，
但大厂品牌也挺重要。

你觉得选哪个？
```

## User goals

```yaml
entrepreneurship: high
ai_native_product: high
brand: medium
compensation: medium
location: Shenzhen_or_HongKong
stability: medium
technical_growth: high
```

## Offer A

```yaml
company_type: large_tech
location: Shenzhen
role: AI Product Manager

compensation:
  monthly: RMB 28000
  months: 16

learning: 3.5
ownership: 2.5
manager_quality: unknown
technical_depth: 3
brand_signal: 5
stability: 4
```

## Offer B

```yaml
company_type: startup
location: Hong_Kong
role: AI Product Engineer

compensation:
  monthly: HKD 35000
  months: 12

learning: 4.5
ownership: 4.5
manager_quality: unknown
technical_depth: 4
brand_signal: 2.5
stability: 2
```

Founder statement:

```text
“你来了什么都能做，客户也可以直接见。”
```

Missing:

```text
written role scope
runway
financing state
real customer volume
manager quality
workload
```

