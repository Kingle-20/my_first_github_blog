// 更稳定的版本 - 使用 CSS 类控制
document.addEventListener("DOMContentLoaded", function () {
  if (document.getElementById('focus-mode-btn')) return;

  // 添加专注模式样式
  const style = document.createElement('style');
  style.textContent = `
    .focus-mode .md-sidebar--primary,
    .focus-mode .md-sidebar--secondary {
      display: none !important;
    }
    .focus-mode .md-main__inner {
      max-width: 100% !important;
      margin: 0 auto !important;
    }
    #focus-mode-btn {
      position: fixed;
      top: 10px;
      right: 10px;
      z-index: 9999;
      padding: 8px 12px;
      background-color: #0066cc;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
    }
    #focus-mode-btn.focus-active {
      background-color: #cc0000;
    }
  `;
  document.head.appendChild(style);

  const button = document.createElement("button");
  button.id = 'focus-mode-btn';
  button.innerText = "专注模式";

  button.addEventListener("click", function () {
    document.body.classList.toggle('focus-mode');
    const isFocus = document.body.classList.contains('focus-mode');
    button.innerText = isFocus ? "退出专注" : "专注模式";
    button.classList.toggle('focus-active', isFocus);
  });

  document.body.appendChild(button);
});
