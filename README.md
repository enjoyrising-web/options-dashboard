# 期权投资看板

## 如何部署

### 1. 上传到 GitHub
把这个文件夹里的所有文件上传到你的 GitHub 仓库 `enjoyrising-web/options-dashboard`。

**操作步骤：**
1. 打开 https://github.com/enjoyrising-web/options-dashboard
2. 点击仓库页面右上角的 **Add file → Upload files**
3. 把这个文件夹里的文件全部拖进去（保持目录结构）
4. 点 **Commit changes**

### 2. 连接 Vercel 部署
1. 打开 https://vercel.com，用 GitHub 账号登录
2. 点 **Add New Project → Import** 选择 `options-dashboard` 仓库
3. 所有设置保持默认，点 **Deploy**
4. 几秒后得到 `https://options-dashboard-xxx.vercel.app` 网址
5. 把这个网址发给任何人，微信里直接打开

### 3. 后续更新数据
每次需要更新数据，只需：
1. 把新数据发给 Claude（上传新 Excel 或告知变化）
2. Claude 生成新的 `data/products.json`
3. 在 GitHub 替换该文件（点击文件 → 编辑 → 粘贴 → Commit）
4. Vercel 自动重新部署，30 秒后网页更新

## 文件结构
```
/
├── index.html          ← 看板主页
├── data/
│   └── products.json   ← 期权数据（每次更新这个文件）
└── vercel.json         ← Vercel 部署配置
```
