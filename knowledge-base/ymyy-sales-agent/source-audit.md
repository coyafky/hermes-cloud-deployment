# Source Audit

## Source

- PDF: `/Users/fkycoya/Downloads/有膜有漾服务手册_复制 (2).pdf`
- Pages: 34
- Text extraction: `pypdf`
- Visual parameter extraction: ImageMagick render + manual transcription from rendered pages

## Extracted Structure

- p.1: 封面
- p.2-p.4: 企业介绍、服务理念、团队风采
- p.5: 服务项目与电脑裁膜
- p.6-p.15: 隐形车衣优势与系列参数
- p.17-p.24: 汽车玻璃膜与窗膜套餐参数
- p.26-p.29: 车身改色膜章节，文本层不足，需继续人工补录
- p.30: 膜面保养小贴士
- p.34: 扫码了解更多

## Data Quality Notes

- PDF 文本层可抽取，但产品参数页大部分参数是图片表格，不在文本层。
- 当前知识库中的隐形车衣与窗膜参数来自页面渲染后的人工转录。
- 窗膜表格原文存在两个同名“紫外线阻隔率”字段，知识库保留为 `紫外线阻隔率_1` 与 `紫外线阻隔率_2`，避免擅自改名。
- 车身改色膜 p.26-p.29 当前只建立章节入口；颜色、系列、价格、质保不做回答。

## Manual Verification Needed

- 复核 p.8-p.15 隐形车衣星级图示，确认是否全部按 5 分制理解。
- 复核 p.18-p.24 窗膜两个“紫外线阻隔率”字段的真实业务含义。
- 补录 p.26-p.29 改色膜产品细项。
- 若后续有新版服务手册，应以新版 PDF 重新生成 source audit。
