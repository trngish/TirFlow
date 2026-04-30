# 预设配置模板说明

本目录包含多个预定义的训练配置文件，可以直接用于 Kohya GUI 或命令行训练。

## 📋 预设列表

### 1. character_portrait.toml - 角色肖像
- **适用场景**：训练人物面部特征
- **推荐图片数**：15-20张
- **Network Dim**：32
- **训练步数**：3000
- **特点**：侧重面部细节，适合角色LoRA入门

### 2. character_fullbody.toml - 角色全身
- **适用场景**：训练人物全身特征
- **推荐图片数**：20-30张
- **Network Dim**：48
- **训练步数**：4000
- **特点**：包含姿态、服装、背景等全身信息

### 3. style_anime.toml - 动漫画风
- **适用场景**：动漫风格训练
- **推荐图片数**：30-50张
- **Network Dim**：64
- **训练步数**：5000
- **特点**：启用色彩增强，学习动漫风格特征

### 4. style_realistic.toml - 写实画风
- **适用场景**：写实风格训练
- **推荐图片数**：25-40张
- **Network Dim**：48
- **训练步数**：4500
- **特点**：保持色彩原样，学习光影质感

### 5. object_product.toml - 产品展示
- **适用场景**：产品图生成
- **推荐图片数**：10-15张
- **Network Dim**：32
- **训练步数**：2500
- **特点**：少量数据即可训练，适合产品展示

### 6. object_clothing.toml - 服装配饰
- **适用场景**：服装、配饰特征
- **推荐图片数**：15-25张
- **Network Dim**：40
- **训练步数**：3000
- **特点**：适合时尚、电商类应用

### 7. expression.toml - 表情姿态
- **适用场景**：表情和姿态训练
- **推荐图片数**：20-30张
- **Network Dim**：24
- **训练步数**：2000
- **特点**：较低维度，快速收敛

### 8. fast_training.toml - 快速训练
- **适用场景**：快速测试迭代
- **推荐图片数**：10-15张
- **Network Dim**：16
- **训练步数**：1000
- **特点**：低分辨率+小维度，适合初步测试

### 9. high_quality.toml - 高质量细节
- **适用场景**：追求最高质量
- **推荐图片数**：30-50张
- **Network Dim**：64
- **训练步数**：8000
- **特点**：长时间训练，效果最佳

## 🚀 使用方法

### 方法1：使用 Kohya GUI
1. 打开 Kohya SS GUI
2. 选择 "LoRA (Easy)" 或 "LoRA (Detailed)" 选项卡
3. 点击 "Config" 标签
4. 点击 "Load config" 按钮
5. 选择 `presets/` 目录下的 `.toml` 文件
6. 根据实际情况修改路径（模型路径、训练数据目录等）
7. 开始训练

### 方法2：命令行训练
```bash
cd sd-scripts
.\venv\Scripts\activate

# 使用预设配置
accelerate launch sdxl_train_network.py --config_file ..\presets\character_portrait.toml

# 或修改后使用
accelerate launch sdxl_train_network.py --config_file ..\presets\style_anime.toml
```

### 方法3：通过 Python 代码加载
```python
import toml

# 加载预设配置
config = toml.load('presets/character_portrait.toml')

# 修改路径
config['model']['pretrained_model_name_or_path'] = 'your/model/path'
config['datasets']['train_data_dir'] = 'your/train/data/path'
config['saving']['output_dir'] = 'your/output/path'
config['saving']['output_name'] = 'your_lora_name'

# 保存并使用
with open('my_config.toml', 'w') as f:
    toml.dump(config, f)
```

## ⚙️ 关键参数说明

### Network Dim (LoRA Rank)
- **16-32**：轻量级，训练快速，容易过拟合
- **48-64**：中等，推荐值，平衡效果和大小
- **128+**：重量级，训练慢，效果强但文件大

### 训练步数
- **1000-2000**：快速测试
- **3000-5000**：标准训练
- **8000+**：高质量追求

### 学习率
- **1e-4**：较高，快速收敛但可能不稳定
- **5e-5**：中等，推荐值
- **1e-5**：较低，慢但稳定

### Noise Offset
- **0.03-0.05**：标准，适合大多数场景
- **0.1+**：增强明暗对比，适合风格训练

## 💡 选择建议

| 场景 | 推荐预设 |
|------|---------|
| 第一次训练 | fast_training.toml |
| 人物角色 | character_portrait.toml |
| 动漫风格 | style_anime.toml |
| 写实风格 | style_realistic.toml |
| 产品展示 | object_product.toml |
| 最高质量 | high_quality.toml |

## ⚠️ 注意事项

1. **修改路径**：所有配置文件中的路径都需要根据实际情况修改
2. **触发词**：sample_prompts 中的 `trigger_word` 需要替换为你的实际触发词
3. **数据质量**：预设只是起点，实际效果取决于训练数据的质量
4. **显存要求**：所有预设都针对 RTX 3060 12GB 优化
5. **备份**：修改配置前建议备份原文件

## 🔧 自定义预设

可以基于现有预设创建自己的预设：

1. 复制一个最接近的预设
2. 根据需求调整参数
3. 保存为新文件
4. 在 config_manager.py 中注册新预设
