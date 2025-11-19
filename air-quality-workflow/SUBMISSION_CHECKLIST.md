# Gradescope 提交检查清单
**学生**: sc22wn
**项目**: Air Quality Monitoring Serverless Workflow
**日期**: 2025-11-19

---

## 📦 提交材料清单

### 1️⃣ 代码文件（必须）

**提交方式**: ZIP 文件或 Git 仓库链接

**包含文件**：
```
air-quality-workflow/
├── GenerateAirQualityData/
│   ├── __init__.py
│   └── function.json
├── ProcessAirQualitySummary/
│   ├── __init__.py
│   └── function.json
├── azure_sql.py
├── local.settings.json
├── host.json
├── requirements.txt
├── README.md
└── (测试脚本)
```

**打包命令** (macOS/Linux):
```bash
cd /Volumes/Mikuu-ultra/Git/DistributedSystem_cw2
zip -r sc22wn_coursework2.zip air-quality-workflow/ \
  -x "*.pyc" \
  -x "*__pycache__/*" \
  -x "*.venv/*" \
  -x "*/.git/*" \
  -x "*.egg-info/*" \
  -x "*node_modules/*"
```

**打包命令** (Windows PowerShell):
```powershell
Compress-Archive -Path air-quality-workflow -DestinationPath sc22wn_coursework2.zip
```

---

### 2️⃣ 文档（必须）

**核心文档**（在 ZIP 中，或单独上传）：
- ✅ `SOLUTION_DESIGN.md` (15KB) - 解决方案设计文档
- ✅ `PERFORMANCE_EVALUATION_REPORT.md` (16KB) - 性能评估报告
- ✅ `README.md` (4.2KB) - 项目说明

**支持文档**：
- ✅ `PROJECT_STATUS.md` (7.1KB) - 项目状态

---

### 3️⃣ 图表（必须）

**架构和设计**：
- ✅ `system_architecture.png` (381KB) - 系统架构图
- ✅ `workflow_diagram.png` (312KB) - 工作流程图

**性能评估**：
- ✅ `performance_charts.png` (414KB) - 性能图表（4个图）
- ✅ `scalability_analysis.png` (219KB) - 可扩展性分析

**数据**：
- ✅ `performance_results.csv` (2.1KB) - 性能测试原始数据

---

### 4️⃣ 视频（必须）

**要求**：
- 时长：最多 2 分钟
- 格式：MP4 或其他常见格式
- 分辨率：1080p 推荐
- 音频：清晰可听

**提交方式**（二选一）：
- [ ] 直接上传到 Gradescope
- [ ] 上传到 YouTube（Unlisted），提交链接

**视频链接格式**（如果用 YouTube）：
```
https://youtu.be/YOUR_VIDEO_ID
或
https://www.youtube.com/watch?v=YOUR_VIDEO_ID
```

---

## 📝 Gradescope 问题准备

### 预期问题和答案

**Q1: Describe your workflow implementation**
**A**:
```
My serverless workflow consists of two Azure Functions:

1. GenerateAirQualityData (Timer Trigger, every 1 min):
   - Simulates IoT sensor data from multiple monitoring stations
   - Generates PM2.5, PM10, O3, and AQI readings
   - Batch inserts data to Azure SQL Database

2. ProcessAirQualitySummary (Timer Trigger, every 2 min):
   - Uses Azure SQL Change Tracking for incremental processing
   - Calculates aggregate statistics (avg AQI, max PM2.5, min O3)
   - Writes summaries to a separate table

The workflow uses Timer Triggers combined with Change Tracking for
reliable and efficient processing.
```

---

**Q2: What performance results did you achieve?**
**A**:
```
Performance Testing Results (11 iterations, 4 configurations):

Load Scenarios:
- 20 records: Avg 12.88s execution time
- 50 records: Avg 23.40s execution time
- 100 records: Avg 40.99s execution time
- 200 records: Avg 66.51s execution time

Key Metrics:
- Throughput: 2.33-3.22 records/second
- Memory Usage: <0.1MB peak consumption
- CPU Utilization: <0.2% average
- Scalability: Load doubles → time increases only 62-82%

Data Scale Validation:
- Successfully accumulated 1,050+ records
- 11 summary aggregations
- 15 monitoring stations
- System remained stable throughout

Conclusion: System demonstrates good scalability and production
readiness.
```

---

**Q3: How did you evaluate scalability?**
**A**:
```
Scalability Evaluation Methodology:

1. Controlled Load Testing:
   - Tested 4 different batch sizes (20, 50, 100, 200 records)
   - 3 iterations per configuration for statistical validity
   - Measured execution time, memory, and CPU for each

2. Scalability Analysis:
   - Calculated load increase vs time increase ratios
   - 20→50: 150% load increase, 81.7% time increase (Good)
   - 50→100: 100% load increase, 75.2% time increase (Good)
   - 100→200: 100% load increase, 62.3% time increase (Excellent)

3. Production-Scale Validation:
   - Cumulative testing with 1,050+ records
   - No performance degradation observed
   - Consistent processing time for aggregation (4-6s)

Result: Sub-linear scaling demonstrates the system can handle
increasing load efficiently.
```

---

**Q4: Show evidence of execution**
**A**:
```
Evidence provided in submission:

1. Performance Test Data:
   - performance_results.csv: Raw test data (11 tests)
   - performance_test_output.txt: Complete test logs

2. Database Validation:
   - 1,050 records in air_quality_data table
   - 11 records in air_quality_summary table
   - 15 unique monitoring stations

3. Visual Evidence:
   - Performance charts showing 4 load scenarios
   - Scalability analysis graphs
   - System architecture diagram

4. Video Demonstration:
   - Shows live database query (1,050 records)
   - Displays performance charts
   - Demonstrates workflow execution

All evidence is reproducible using provided scripts:
- python performance_test.py
- python quick_validation.py
```

---

**Q5: What technologies did you use?**
**A**:
```
Technology Stack:

Cloud Platform:
- Microsoft Azure (East US region)
- Azure Functions (Python 3.11 runtime)
- Azure SQL Database (General Purpose Serverless, 1 vCore)

Programming:
- Python 3.11
- pyodbc for database connectivity
- azure-identity for authentication

Database Features:
- Azure SQL Change Tracking for incremental processing
- Transaction management for data consistency
- Auto-scaling serverless tier

Monitoring & Testing:
- Python psutil for performance monitoring
- Custom test framework for load testing
- matplotlib/pandas for visualization
```

---

**Q6: What challenges did you face?**
**A**:
```
Key Challenges and Solutions:

1. Database Connectivity:
   Challenge: Azure AD MFA requirements
   Solution: Switched to SQL Server authentication for development

2. ODBC Driver Configuration (macOS):
   Challenge: Driver not detected by pyodbc
   Solution: Set ODBCSYSINI environment variable to driver path

3. Performance at Scale:
   Challenge: Ensuring consistent performance with growing data
   Solution: Implemented batch operations and Change Tracking

4. Trigger Mechanism:
   Challenge: Azure SQL Triggers not directly available
   Solution: Used Timer + Change Tracking hybrid approach

These challenges taught me about cloud authentication,
database optimization, and serverless architecture design.
```

---

## ✅ 提交前最终检查

### 代码部分
- [ ] 所有函数代码已包含
- [ ] requirements.txt 完整
- [ ] local.settings.json 已清理敏感信息（或用示例配置）
- [ ] README.md 包含运行说明
- [ ] ZIP 文件大小合理（<50MB）

### 文档部分
- [ ] SOLUTION_DESIGN.md 完整
- [ ] PERFORMANCE_EVALUATION_REPORT.md 完整
- [ ] 所有图表清晰可读
- [ ] 引用了相关的 Azure 文档

### 视频部分
- [ ] 时长 <2 分钟
- [ ] 音质清晰
- [ ] 画质清晰（1080p）
- [ ] 展示了真实数据（1050+ 条）
- [ ] 展示了性能图表
- [ ] 上传成功（或链接有效）

### 问答部分
- [ ] 准备了实施描述
- [ ] 准备了性能结果说明
- [ ] 准备了可扩展性分析
- [ ] 准备了执行证据
- [ ] 准备了技术栈说明

---

## 📊 预期评分

| 评分项 | 满分 | 预计得分 | 完成度 |
|--------|------|----------|--------|
| Workflow originality | 5 | 5 | 100% ✓ |
| Solution Design | 10 | 9-10 | 95% ✓ |
| Implementation | 15 | 15 | 100% ✓ |
| Evaluation | 10 | 10 | 100% ✓ |
| Code/scripts | 5 | 5 | 100% ✓ |
| Video | 5 | 5 | 100% ✓ |
| **总计** | **50** | **49-50** | **98-100%** ✓ |

---

## 📧 提交信息

**Gradescope 课程**: COMP3211 / XJCO3211
**作业**: Coursework 2 - Serverless Workflow
**学生 ID**: sc22wn
**提交截止日期**: [检查 Gradescope]

---

## 🎯 最后提醒

1. **不要在最后一刻提交**：留出时间处理可能的技术问题
2. **保留备份**：提交前备份所有文件
3. **检查文件名**：确保清晰易识别
4. **测试链接**：如果提交视频链接，先在隐私窗口测试
5. **截图确认**：提交成功后截图保存

---

**Good luck! 你已经完成了一个出色的项目！🚀**

**最终得分预测**: 49-50/50 (满分！) 🎉
