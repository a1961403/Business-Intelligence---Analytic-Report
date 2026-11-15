# 上传与报告补充说明

## 怎么上传
1. 解压 ZIP；在 GitHub 新建仓库。
2. 将本文件夹里面的文件和 data、evidence 文件夹上传到仓库根目录，不要只上传 ZIP。
3. 使用本地 Git 或 GitHub 的文件上传功能均可。确认 README、analyse_aq2.py、data 和 evidence 都能打开。
4. 点击仓库地址栏复制真实地址。若是私有仓库，需要确保队友及阅卷老师有访问权限。
5. 将实际地址发回，可再替换报告 Appendix C 中的说明。不要提交下文的方括号占位符。

## Appendix C1 可替换文字（取得真实地址后）

The reproducibility package is available at [INSERT ACTUAL REPOSITORY URL]. It contains the cleaned cohort, preparation script and audit, AQ2 analysis code, complete numerical evidence, and figure-generation scripts. After installing the dependencies in requirements.txt, run python run_all.py to regenerate the AQ2 outputs and verify them against the report evidence. Rebuilding the cleaned cohort from scratch additionally requires the original source files described in the repository README; these full source files are not included.

原文“尚未提供仓库地址”不是要求伪造地址；课程所贴任务要求也没有强制 GitHub。若最终随作业交附件包，也可写明真实附件名称而不用仓库链接。

## 检查到的其他依赖
- Section 2 是队友的数据说明：个人文稿中的交叉引用要在最终合并版中核对。
- Appendix D1 引用了完整结果与随附证据：本包已提供这些数值文件。
- Assignment 1 的 4,576、640 等旧值：需要对照真实 A1 文稿确认；旧代码缺失无法补造。
- 原始大文件：本包未包含；可按 README 获取相同版本。现有清洗后数据足以复现 AQ2。
- 独立样本验证、专家评审、扩大时间范围：属于建议，不是遗漏的已完成成果。
- AQ1、AQ3、AQ4 结果与团队最终解释：仍由相应队友补齐，本包只覆盖 Member 1。

## 建议补充的一句适用范围说明

Although the intended client is US-based, the analytical cohort includes postings collected under United States, United Kingdom, Canada and Australia search settings. The pooled results should therefore be treated as cross-market exploratory benchmarks rather than representative estimates of the US labour market.

依据：清洗数据 search_country 分别为 1480、196、137、116 条。该字段不能直接当作已核实的真实工作地点。如只分析美国，需要重新筛选并重算，不能仅修改文字或沿用当前数字。
