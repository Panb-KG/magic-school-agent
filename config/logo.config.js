# Logo配置文件

## 📋 基本信息

**Logo名称**: 魔法书AI核心
**文件名**: 魔法书AI核.jpg
**文件路径**: `assets/魔法书AI核.jpg`
**文件大小**: 612KB
**格式**: JPG
**创建日期**: 2024

---

## 🎨 设计说明

### 核心元素
1. **魔法书**: 象征知识、智慧、传承
2. **发光水晶球**: 象征AI的洞察力和预测能力
3. **AI标识**: 明确智能体身份
4. **魔法符号**: 弯月、圆环、五芒星、音符等

### 色彩
- **深蓝色**: 神秘、浩瀚
- **金色**: 精致、仪式感
- **冰蓝色**: 科技、灵动

### 风格
奇幻魔法风 + 科技感融合

---

## 📐 推荐尺寸

根据使用场景，推荐以下尺寸：

| 场景 | 尺寸 | 说明 |
|------|------|------|
| 网站Logo | 40x40 | 网站头部Logo |
| 对话头像-小 | 32x32 | 聊天气泡内头像 |
| 对话头像-中 | 48x48 | 对话列表头像 |
| 对话头像-大 | 64x64 | 用户详情头像 |
| 图标 | 128x128 | 应用图标 |
| 海报 | 1024x1024 | 宣传海报 |
| Favicon | 32x32 | 浏览器标签页图标 |

---

## 🔗 使用路径

### 相对路径
```javascript
// 前端代码中使用
import logoImage from '@/assets/魔法书AI核.jpg';
```

### 绝对路径
```javascript
// 在不同环境中使用
const logoPath = '/assets/魔法书AI核.jpg';
```

### 配置路径
```javascript
// 在配置文件中定义
export const LOGO_PATH = 'assets/魔法书AI核.jpg';
export const LOGO_URL = `/${LOGO_PATH}`;
```

---

## 📝 使用规范

### ✅ 允许的操作

1. **等比例缩放**
   - 保持原始比例
   - 不拉伸或压缩

2. **调整尺寸**
   - 根据实际需求调整大小
   - 保持清晰度

3. **添加阴影**
   - 可以添加轻微的阴影效果
   - 增强立体感

4. **添加边框**
   - 可以添加圆形或圆角边框
   - 用于对话头像等场景

### ❌ 禁止的操作

1. **修改颜色**
   - 不得更改Logo的原始颜色

2. **删除元素**
   - 不得移除任何设计元素

3. **添加元素**
   - 不得在Logo上添加额外内容

4. **旋转或翻转**
   - 不得旋转或翻转Logo

5. **拉伸变形**
   - 不得改变Logo的宽高比

---

## 🌐 品牌应用

### 数字媒体

**网站**
- 顶部导航栏Logo
- 网站Footer
- 登录/注册页

**移动应用**
- 应用图标
- 启动页
- 对话界面头像

**社交媒体**
- 头像
- 封面图
- 发布图片水印

### 印刷媒体

**名片**
- 公司Logo位置

**宣传册**
- 封面Logo
- 内页标识

**海报**
- 主视觉元素
- 品牌标识

---

## 🎯 使用示例

### 前端React组件

```tsx
import React from 'react';
import logoImage from '@/assets/魔法书AI核.jpg';

const AppLogo: React.FC = () => {
  return (
    <img
      src={logoImage}
      alt="魔法课桌AI助手"
      className="app-logo"
      width={40}
      height={40}
    />
  );
};

export default AppLogo;
```

### CSS样式

```css
.app-logo {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.app-logo:hover {
  transform: scale(1.05);
}
```

### 配置文件

```javascript
// config/logo.js
export const LOGO = {
  path: 'assets/魔法书AI核.jpg',
  alt: '魔法课桌AI助手',
  title: '魔法课桌',
  // 对话头像配置
  chat: {
    small: { width: 32, height: 32 },
    medium: { width: 48, height: 48 },
    large: { width: 64, height: 64 },
  },
  // 网站Logo配置
  website: {
    height: 40,
  },
};
```

---

## 📚 相关文档

- [Logo说明文档](./Logo说明.md) - 详细的设计理念和使用规范
- [前端Logo集成指南](./前端Logo集成指南.md) - 前端集成示例
- [README.md](../README.md) - 项目总览

---

## 📞 品牌咨询

如需使用Logo用于商业用途或需要不同格式的Logo文件，请联系项目团队。

---

**配置版本**: 1.0.0
**最后更新**: 2024
**项目**: 魔法课桌学习助手智能体
