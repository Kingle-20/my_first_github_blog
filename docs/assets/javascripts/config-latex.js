window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    processEscapes: true,
    packages: {'[+]': ['ams']},
    tags: 'ams',           // 关键：启用 AMS 风格的公式编号
    tagSide: 'right',      // 编号显示在右侧
    useLabelIds: true,     // 使用标签 ID
    ams: {
      multlineWidth: '100%', // AMS 多行公式宽度
      tags: 'ams'           // AMS 标签设置
    }
  },
  loader: {
    load: ['[tex]/ams']    // 确保加载 AMS 包
  },
  options: {
    skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
  },
  startup: {
    typeset: true          // 启动时自动排版
  }
};
