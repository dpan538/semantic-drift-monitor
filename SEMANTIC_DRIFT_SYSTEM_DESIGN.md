# 商业语义漂移实验系统设计

## 1. 研究目标

本系统用于防晒与 SPF 护肤品类中的商业语义漂移检测，并评估商品潜力衰减的早期信号。

核心研究问题：

> 在防晒与 SPF 护肤产品中，围绕 natural、clean、gentle、sensitive、dermatologist、reef safe 等安全感与温和性话术的宣传强化，是否会在后续消费者评论中表现为更高怀疑率、更多性价比抱怨、更弱复购表达、更多清晰度问题，或更窄的使用场景？

第一阶段不把“商品潜力衰减”做成一个黑箱总分，而是拆成多个可观察结果变量：

- trust erosion：怀疑、不信任、营销感、虚假评论、网红带货疑虑。
- value decline：贵、不值、溢价、买品牌、浪费钱。
- clarity loss：不知道适合谁、怎么用、是否可叠加妆容、是否真的防晒。
- repeatability weakness：不会回购、只试一次、没必要再买。
- use-case narrowing：使用场景越来越集中，例如只适合妆前、只适合拍照、只适合短时通勤。

## 2. 对参考脚本的关键修正

参考脚本适合作为原型，但直接用于研究会有几个风险。本设计做如下调整。

### 2.1 从“实时告警系统”改为“研究型面板流水线”

告警适合产品监控，但论文第一阶段更需要：

- 可复现数据表。
- 可审计指标定义。
- 可手工验证的标注样本。
- 可运行固定效应模型和事件研究的产品-月份面板。

因此第一阶段只保留日志，不启用邮件告警。告警系统放到第二阶段。

### 2.2 避免复合指标循环

参考脚本中的 attenuation_index 把 semantic_gap、skepticism、value complaint、entropy decline 合并为一个分数。第一篇研究中不建议这样做，因为 drift 指标和 attenuation outcome 容易互相污染。

本设计采用：

- Drift predictors：宣传密度、抽象性、关键词饱和度、宣传-评论语义差距、宣传-评论属性差距。
- Attenuation outcomes：怀疑率、性价比抱怨率、复购弱化率、清晰度问题率、场景熵。

复合指数仅作为探索性附录或第二阶段验证后的 latent construct。

### 2.3 修正关键词匹配方式

参考脚本中 `text.lower().split()` 无法正确识别多词短语，例如：

- "broad spectrum"
- "dermatologist tested"
- "not worth it"
- "white cast"
- "marketing gimmick"

本系统必须使用短语级匹配：

- 正则 phrase matcher。
- 可选 spaCy PhraseMatcher。
- 统一记录匹配位置、类别、来源字段和时间。

### 2.4 语义差距不能只用整段平均 embedding

整段 promo 与所有 review 做平均余弦距离太粗，会受到评论主题偏移影响。第一阶段保留两层指标：

- coarse semantic gap：promo text 与 review text 的整体 embedding 距离。
- aspect gap：同一属性上的宣传强度与评论情感差，例如 sunscreen protection、white cast、greasiness、irritation、makeup layering。

论文主结果优先使用 aspect gap，因为它更可解释。

### 2.5 历史商品页不可得的问题

Amazon 等平台的历史评论通常可以回溯，但历史标题、描述、图片、badge 不一定能稳定回溯 24 个月。

因此数据设计拆成两层：

- Retrospective layer：回溯 24 个月评论、评分、价格、评论数、可得的 rank/price proxy。
- Prospective layer：从项目开始后，每月抓取商品页、图片 OCR、标题、描述、bullet points、价格和评分。

如果历史商品页无法获得，第一篇仍可用“当前宣传强度 + 历史评论轨迹”做 feasibility pilot，但正式因果叙述必须谨慎。

## 3. 推荐项目结构

```text
semantic_drift_monitor/
  README.md
  pyproject.toml
  config/
    settings.yaml
    lexicons/
      promo_sunscreen_en.yaml
      skepticism_en.yaml
      value_en.yaml
      scenarios_sunscreen_en.yaml
      aspects_sunscreen_en.yaml
  data/
    raw/
      product_pages/
      reviews/
      qa/
      images/
    interim/
      cleaned_text/
      extracted_claims/
      matched_terms/
      annotations/
    processed/
      product_master.parquet
      promo_snapshot.parquet
      promo_claim.parquet
      review.parquet
      review_sentence.parquet
      review_flags.parquet
      product_month_panel.parquet
    audit/
      collection_log.parquet
      robots_tos_notes.md
      manual_validation_samples.csv
  src/
    semantic_drift/
      __init__.py
      collect/
        base.py
        amazon_adapter.py
        public_dataset_adapter.py
        snapshot_writer.py
      clean/
        normalize.py
        segment.py
        dedupe.py
        time_align.py
      lexicon/
        loader.py
        phrase_matcher.py
      claims/
        extract.py
        classify.py
      reviews/
        sentence_flags.py
        aspects.py
        scenarios.py
        repurchase.py
      metrics/
        promo_intensity.py
        abstractness.py
        semantic_gap.py
        aspect_gap.py
        skepticism.py
        value.py
        lockin.py
        panel_builder.py
      models/
        fixed_effects.py
        event_study.py
        robustness.py
      evaluation/
        annotation_export.py
        agreement.py
        classifier_eval.py
      viz/
        descriptive.py
        event_plots.py
  scripts/
    01_build_product_master.py
    02_collect_or_import_reviews.py
    03_collect_current_snapshots.py
    04_clean_text.py
    05_extract_claims_and_flags.py
    06_build_monthly_panel.py
    07_run_descriptives.py
    08_run_models.py
  notebooks/
    01_feasibility_check.ipynb
    02_metric_validation.ipynb
    03_panel_results.ipynb
  outputs/
    figures/
    tables/
    reports/
```

## 4. 数据表设计

### 4.1 product_master

单位：SKU。

字段：

- product_id
- platform
- asin_or_sku
- brand
- product_name
- category
- subcategory
- spf_value
- mineral_or_chemical
- size_ml_or_oz
- launch_date_if_available
- product_url
- active_flag

### 4.2 promo_snapshot

单位：产品页面快照。

字段：

- snapshot_id
- product_id
- capture_date
- source
- title
- bullet_points
- description
- a_plus_content
- image_ocr_text
- price
- rating_avg
- rating_count
- review_count
- sales_rank_proxy
- raw_html_path
- clean_text

### 4.3 promo_claim

单位：抽取出的宣传声明。

字段：

- claim_id
- snapshot_id
- product_id
- capture_date
- claim_text
- claim_type：efficacy / sensorial / natural_clean / premium / clinical / identity
- target_aspect：protection / irritation / white_cast / greasiness / makeup / water_resistance / acne / aging
- matched_terms
- abstractness_score
- evidence_marker_flag
- certainty_marker_flag
- regulatory_marker_flag

### 4.4 review

单位：单条评论。

字段：

- review_id
- product_id
- review_date
- rating
- verified_purchase
- title
- review_text
- helpful_votes
- reviewer_meta_if_available
- collection_date

### 4.5 review_sentence

单位：评论句子。

字段：

- sentence_id
- review_id
- product_id
- review_date
- sentence_text
- aspect
- sentiment
- matched_terms
- skepticism_flag
- value_complaint_flag
- clarity_issue_flag
- repurchase_negative_flag
- repurchase_positive_flag
- scenario_labels

### 4.6 product_month_panel

单位：产品 × 月份。

字段：

- product_id
- month
- promo_density_total
- promo_density_natural_clean
- promo_density_premium
- abstractness_ratio
- claim_diversity
- semantic_gap_coarse
- aspect_gap_protection
- aspect_gap_irritation
- aspect_gap_white_cast
- review_count_month
- avg_rating_month
- skepticism_ratio
- value_complaint_ratio
- clarity_issue_ratio
- negative_repurchase_ratio
- positive_repurchase_ratio
- scenario_entropy
- price
- discount_pct
- rating_avg
- rating_count

## 5. 词典设计

词典不应写死在 Python 文件中，而应保存在 YAML 中，方便迭代和人工审计。

### 5.1 promo_sunscreen_en.yaml

```yaml
efficacy:
  - broad spectrum
  - uva
  - uvb
  - spf 30
  - spf 50
  - water resistant
  - sweat resistant
  - non-comedogenic
  - dark spot
  - hyperpigmentation

sensorial:
  - lightweight
  - non-greasy
  - fast absorbing
  - invisible
  - no white cast
  - matte finish
  - dewy
  - glow
  - silky

natural_clean:
  - natural
  - clean
  - mineral
  - zinc oxide
  - titanium dioxide
  - reef safe
  - vegan
  - cruelty free
  - fragrance free
  - hypoallergenic
  - gentle
  - sensitive skin

clinical_premium:
  - dermatologist tested
  - dermatologist recommended
  - medical grade
  - clinical
  - advanced
  - professional
  - luxury
  - premium
```

### 5.2 skepticism_en.yaml

```yaml
overclaim:
  - overhyped
  - too good to be true
  - gimmick
  - marketing gimmick
  - just marketing
  - all hype

authenticity:
  - fake reviews
  - paid promotion
  - influencer
  - sponsored
  - scam

inefficacy:
  - did nothing
  - no difference
  - still burned
  - broke me out
  - irritated
  - stings
  - pills
  - white cast
  - greasy
  - sticky
```

### 5.3 value_en.yaml

```yaml
price_complaint:
  - overpriced
  - not worth it
  - waste of money
  - expensive for nothing
  - pay for the brand
  - too expensive
  - cheaper options
```

### 5.4 scenarios_sunscreen_en.yaml

```yaml
daily_use:
  - everyday
  - daily
  - morning routine
  - commute
  - work

outdoor_sports:
  - beach
  - pool
  - hiking
  - running
  - sweat
  - sports

makeup_layering:
  - under makeup
  - under foundation
  - primer
  - concealer

sensitive_skin:
  - rosacea
  - eczema
  - reactive skin
  - sensitive skin
  - post procedure

family_use:
  - baby
  - kids
  - children
  - family
```

## 6. 指标设计

### 6.1 Drift predictors

#### 宣传密度

每 100 个词中宣传关键词或短语的出现次数。

```text
promo_density = matched_promo_terms / token_count * 100
```

需要分类型计算：

- promo_density_total
- promo_density_natural_clean
- promo_density_clinical_premium
- promo_density_sensorial
- promo_density_efficacy

#### 抽象性比例

使用 Brysbaert concreteness norms 或研究自建词典。低具体性词占比越高，抽象性越强。

```text
abstractness_ratio = low_concreteness_terms / matched_terms_or_tokens
```

注意：第一阶段不把 unknown words 默认视为抽象。unknown 应单独记录，否则会夸大抽象性。

#### 粗粒度语义差距

同一产品同一月份中，promo snapshot 与后续评论文本的 embedding 距离。

```text
semantic_gap = 1 - cosine_similarity(embedding(promo), embedding(reviews))
```

建议只作为辅助指标。

#### 属性级宣传-评论差距

对 sunscreen 更关键的是属性级 gap：

```text
aspect_gap_a = promo_claim_intensity_a - review_sentiment_a
```

例如：

- protection：宣传 SPF / broad spectrum，但评论出现 still burned。
- irritation：宣传 gentle / sensitive skin，但评论出现 stings / broke me out。
- white_cast：宣传 invisible / no white cast，但评论出现 white cast。
- makeup：宣传 under makeup / primer-like，但评论出现 pills / peels。

### 6.2 Attenuation outcomes

#### 怀疑率

产品-月份内，被标记为怀疑、不信任、营销感、虚假评论疑虑的句子比例。

```text
skepticism_ratio = skeptical_sentences / total_review_sentences
```

#### 性价比抱怨率

```text
value_complaint_ratio = value_complaint_sentences / total_review_sentences
```

#### 清晰度问题率

包括不理解用途、用法、适用肤质、适用场景、宣传到底是什么意思。

```text
clarity_issue_ratio = clarity_issue_sentences / total_review_sentences
```

#### 复购弱化率

```text
negative_repurchase_ratio = negative_repurchase_sentences / total_review_sentences
positive_repurchase_ratio = positive_repurchase_sentences / total_review_sentences
```

#### 场景熵

场景越多样，熵越高；越锁定在一个狭窄用途，熵越低。

```text
scenario_entropy = -sum(p_s * log(p_s)) / log(number_of_scenarios)
```

## 7. 统计设计

### 7.1 Feasibility pilot

第一轮先做 50-80 个 SKU，而不是直接 300 个。

通过标准：

- 至少 60% SKU 有 24 个月内评论。
- 至少 60% SKU 每个活跃月份有 5 条以上评论，或总评论数大于 50。
- natural / clean / gentle / dermatologist 等关键词在 promo 或 reviews 中有足够出现。
- 怀疑、价值、清晰度、复购、场景指标不是全 0 或极端稀疏。

### 7.2 产品-月份固定效应模型

主模型：

```text
Y_it = alpha_i + gamma_t + beta * Drift_i,t-1 + theta * Controls_it + epsilon_it
```

其中：

- i：产品。
- t：月份。
- alpha_i：产品固定效应。
- gamma_t：月份固定效应。
- Drift_i,t-1：滞后一月的语义漂移或宣传强度指标。
- Y_it：怀疑率、性价比抱怨率、清晰度问题率、复购弱化率、场景熵。

控制变量：

- price
- discount_pct
- rating_avg
- rating_count
- review_count_month
- spf_value
- mineral_or_chemical
- brand or product fixed effect
- verified_purchase_share

对于比例型结果，第一阶段可用按评论数加权的 OLS；稳健性检验使用 fractional logit 或 binomial GLM。

### 7.3 事件研究

当产品页面新增或显著增加关键词时，例如 natural、clean、dermatologist recommended：

```text
Y_it = alpha_i + gamma_t + sum_k beta_k * EventTime_k + controls_it + epsilon_it
```

观察事件前后三个月：

- 怀疑率是否上升。
- 价值抱怨是否上升。
- 场景熵是否下降。
- 复购弱化是否上升。

## 8. 人工验证设计

第一阶段至少做两类人工验证。

### 8.1 怀疑句验证

抽样：

- 200-500 个评论句子。
- 覆盖高宣传密度和低宣传密度产品。
- 覆盖不同月份。

标注标签：

- skepticism
- value complaint
- clarity issue
- repurchase positive
- repurchase negative
- scenario label

评估：

- Cohen's kappa：双人标注一致性。
- precision / recall / F1：词典或小模型预测效果。

### 8.2 Claim taxonomy 验证

抽样：

- 100-200 个宣传 claim。

标注标签：

- claim_type
- target_aspect
- evidence_marker
- abstractness_level

若 claim_type 一致性低，则先修词典和分类规则，再扩大样本。

## 9. 证伪标准

必须在研究设计中写清楚以下证伪条件。

### 9.1 主假设不成立

如果控制产品、月份、价格、评分、评论量后，高宣传密度或高抽象性产品并未表现出：

- 更高怀疑率；
- 更高性价比抱怨率；
- 更高清晰度问题率；
- 更弱复购表达；
- 更低场景熵；

则“宣传强化导致潜力衰减”的主假设在该样本中不成立。

### 9.2 关键词疲劳不成立

如果 natural / clean / gentle 等关键词的促销使用频率上升后，评论中的关键词周边情感并未下降，怀疑共现也未增加，则关键词疲劳假设不成立。

### 9.3 替代解释

如果所有负面变化主要由价格上涨、折扣消失、包装改版、产品配方变更、季节性防晒需求或平台评论政策变化解释，则语义漂移解释需要降级。

## 10. 实施顺序

### Week 1：数据可得性验证

- 选 Amazon US 作为第一平台。
- 建立 50-80 个 sunscreen / SPF skincare SKU 清单。
- 记录产品 URL、ASIN、品牌、SPF、价格、评分、评论数。
- 明确采集方式：官方 API、合规第三方 API、公开数据集，或人工导入。

### Week 2：评论导入与清洗

- 导入过去 24 个月评论。
- 保留 review_date、rating、verified_purchase、review_text。
- 分句、去重、语言检测。

### Week 3：词典匹配与 claim 抽取

- 实现 phrase matcher。
- 从当前商品页抽取宣传关键词与 claim。
- 对评论句子打 skepticism、value、clarity、repurchase、scenario 标签。

### Week 4：指标面板

- 构建 product_month_panel。
- 计算 8 个核心指标。
- 检查缺失、稀疏、极端值。

### Week 5：人工验证

- 导出标注样本。
- 计算 kappa、precision、recall、F1。
- 修正词典和规则。

### Week 6：描述性图表

- promo_density vs skepticism_ratio。
- natural_clean_density vs value_complaint_ratio。
- aspect_gap_irritation vs negative review trend。
- scenario_entropy over time。

### Week 7-8：统计模型

- 跑产品-月份固定效应。
- 做滞后一月 Drift predictor。
- 如果有页面变更事件，做事件研究。

## 11. 第一阶段最小可运行版本

第一阶段只实现以下脚本：

```text
scripts/01_build_product_master.py
scripts/02_import_reviews.py
scripts/03_import_or_collect_current_snapshots.py
scripts/04_clean_text.py
scripts/05_match_lexicons.py
scripts/06_build_monthly_panel.py
scripts/07_validate_metrics.py
scripts/08_run_descriptives.py
```

暂不实现：

- 邮件告警。
- 大规模代理爬虫。
- Granger causality。
- diachronic word embeddings。
- 自动复合 attenuation index。

这些放到第二阶段。

## 12. 结论

最佳执行路线不是先写一个“监控告警工具”，而是先做一个可复现的研究流水线：

1. 建 product_master。
2. 导入或合规采集评论。
3. 抓取当前商品页快照并从今天开始做纵向 snapshot。
4. 用短语级词典抽取宣传 claim 与消费者反应。
5. 构建 product-month panel。
6. 先验证指标，再跑固定效应模型。

这样既能保留参考脚本的工程可执行性，又能满足论文审稿人最关心的识别逻辑、测量有效性和证伪标准。
