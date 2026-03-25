"""
原材料成本与损耗率关联分析可视化方案
=====================================
本方案聚焦成本与损耗率关联分析，围绕三大维度展开：
1. 成本分布可视化
2. 损耗率高低可视化
3. 损耗原因对成本的影响可视化
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ==========================================
# 第一部分：生成原材料数据集
# ==========================================

def generate_material_data():
    """
    生成原材料数据集
    字段：原材料名称、品类、采购单价、月使用量、总成本、损耗率、损耗原因、采购批次
    """
    np.random.seed(42)

    # 定义原材料数据
    materials_data = []

    # 主料（高价值，中等损耗）
    main_materials = [
        ('牛肉', 85.0, 500, 2.5, ['存储不当', '加工工艺', '运输破损']),
        ('猪肉', 35.0, 800, 3.2, ['存储不当', '加工工艺']),
        ('鸡肉', 18.0, 1200, 2.8, ['加工工艺', '运输破损']),
        ('三文鱼', 120.0, 200, 4.5, ['存储不当', '运输破损']),
        ('虾仁', 95.0, 300, 3.8, ['存储不当', '加工工艺']),
        ('进口牛排', 280.0, 150, 2.0, ['存储不当', '运输破损']),
        ('羊肉', 75.0, 250, 3.5, ['加工工艺', '存储不当']),
        ('鸭肉', 28.0, 400, 4.0, ['加工工艺', '运输破损']),
    ]

    # 辅料（中等价值，较低损耗）
    auxiliary_materials = [
        ('食用盐', 3.5, 500, 1.2, ['存储不当']),
        ('白砂糖', 8.0, 400, 1.5, ['存储不当', '运输破损']),
        ('生抽酱油', 15.0, 200, 2.0, ['运输破损']),
        ('老抽酱油', 18.0, 150, 2.2, ['运输破损']),
        ('料酒', 12.0, 180, 1.8, ['运输破损']),
        ('白醋', 6.0, 220, 2.5, ['运输破损', '存储不当']),
        ('蚝油', 22.0, 120, 3.0, ['存储不当']),
        ('豆瓣酱', 16.0, 100, 2.8, ['存储不当']),
        ('花椒', 85.0, 50, 4.5, ['存储不当', '加工工艺']),
        ('八角', 65.0, 40, 3.5, ['存储不当']),
        ('生姜', 12.0, 300, 8.0, ['存储不当', '加工工艺']),
        ('大蒜', 8.0, 400, 6.5, ['存储不当', '加工工艺']),
        ('葱', 6.0, 350, 10.0, ['存储不当', '加工工艺']),
        ('香菜', 15.0, 80, 12.0, ['存储不当', '加工工艺']),
    ]

    # 包装材料（低价值，中等损耗）
    packaging_materials = [
        ('食品级塑料袋', 0.15, 5000, 3.5, ['运输破损', '存储不当']),
        ('真空包装袋', 0.45, 3000, 2.8, ['运输破损']),
        ('纸箱', 2.5, 2000, 5.5, ['运输破损', '存储不当']),
        ('泡沫箱', 8.0, 800, 4.0, ['运输破损']),
        ('保鲜膜', 12.0, 600, 2.5, ['存储不当']),
        ('铝箔纸', 25.0, 300, 3.0, ['运输破损']),
        ('食品标签', 0.08, 10000, 1.5, ['存储不当']),
        ('打包带', 15.0, 400, 4.5, ['运输破损']),
    ]

    # 采购批次
    batches = ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06']

    # 生成主料数据
    for name, unit_price, base_qty, base_loss_rate, loss_reasons in main_materials:
        for batch in batches:
            # 添加随机波动
            qty_variation = np.random.uniform(0.8, 1.2)
            loss_variation = np.random.uniform(0.7, 1.3)

            monthly_usage = int(base_qty * qty_variation)
            loss_rate = round(base_loss_rate * loss_variation, 2)
            loss_rate = min(loss_rate, 15.0)  # 限制最大损耗率

            total_cost = round(unit_price * monthly_usage, 2)
            loss_reason = np.random.choice(loss_reasons)

            materials_data.append({
                '原材料名称': name,
                '品类': '主料',
                '采购单价': unit_price,
                '月使用量': monthly_usage,
                '总成本': total_cost,
                '损耗率': loss_rate,
                '损耗原因': loss_reason,
                '采购批次': batch
            })

    # 生成辅料数据
    for name, unit_price, base_qty, base_loss_rate, loss_reasons in auxiliary_materials:
        for batch in batches:
            qty_variation = np.random.uniform(0.85, 1.15)
            loss_variation = np.random.uniform(0.8, 1.2)

            monthly_usage = int(base_qty * qty_variation)
            loss_rate = round(base_loss_rate * loss_variation, 2)
            loss_rate = min(loss_rate, 15.0)

            total_cost = round(unit_price * monthly_usage, 2)
            loss_reason = np.random.choice(loss_reasons)

            materials_data.append({
                '原材料名称': name,
                '品类': '辅料',
                '采购单价': unit_price,
                '月使用量': monthly_usage,
                '总成本': total_cost,
                '损耗率': loss_rate,
                '损耗原因': loss_reason,
                '采购批次': batch
            })

    # 生成包装材料数据
    for name, unit_price, base_qty, base_loss_rate, loss_reasons in packaging_materials:
        for batch in batches:
            qty_variation = np.random.uniform(0.9, 1.1)
            loss_variation = np.random.uniform(0.85, 1.15)

            monthly_usage = int(base_qty * qty_variation)
            loss_rate = round(base_loss_rate * loss_variation, 2)
            loss_rate = min(loss_rate, 10.0)

            total_cost = round(unit_price * monthly_usage, 2)
            loss_reason = np.random.choice(loss_reasons)

            materials_data.append({
                '原材料名称': name,
                '品类': '包装材料',
                '采购单价': unit_price,
                '月使用量': monthly_usage,
                '总成本': total_cost,
                '损耗率': loss_rate,
                '损耗原因': loss_reason,
                '采购批次': batch
            })

    df = pd.DataFrame(materials_data)

    # 计算损耗成本
    df['损耗成本'] = round(df['总成本'] * df['损耗率'] / 100, 2)

    return df


# ==========================================
# 第二部分：成本分布可视化
# ==========================================

def plot_cost_distribution(df):
    """
    第一维度：成本分布可视化
    - 品类成本占比饼图
    - 单种原材料成本排序柱状图
    """
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle('第一维度：成本分布可视化', fontsize=20, fontweight='bold', y=0.98)
    plt.subplots_adjust(hspace=0.35, wspace=0.3)

    # 1. 品类成本占比饼图
    ax1 = axes[0, 0]
    category_cost = df.groupby('品类')['总成本'].sum().sort_values(ascending=False)
    colors_pie = ['#FF6B6B', '#4ECDC4', '#45B7D1']

    wedges, texts, autotexts = ax1.pie(
        category_cost.values,
        labels=category_cost.index,
        autopct='%1.1f%%',
        colors=colors_pie,
        explode=[0.02, 0.02, 0.02],
        shadow=True,
        startangle=90
    )
    ax1.set_title('品类总成本占比分布', fontsize=16, fontweight='bold', pad=20)

    # 美化百分比文字
    for autotext in autotexts:
        autotext.set_fontsize(12)
        autotext.set_fontweight('bold')

    # 添加图例
    total_cost = category_cost.sum()
    legend_labels = [f'{cat}: ¥{cost:,.0f} ({cost/total_cost*100:.1f}%)'
                     for cat, cost in category_cost.items()]
    ax1.legend(wedges, legend_labels, title="成本明细", loc="center left",
               bbox_to_anchor=(1.05, 0.5), fontsize=11, title_fontsize=12)

    # 2. 品类成本柱状图（带数值标签）
    ax2 = axes[0, 1]
    bars = ax2.bar(category_cost.index, category_cost.values, color=colors_pie, edgecolor='white', linewidth=2)
    ax2.set_title('品类总成本对比', fontsize=16, fontweight='bold', pad=20)
    ax2.set_ylabel('总成本 (元)', fontsize=13)
    ax2.set_xlabel('品类', fontsize=13)
    ax2.tick_params(axis='both', labelsize=11)

    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'¥{height:,.0f}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    # 添加网格线
    ax2.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax2.set_axisbelow(True)

    # 3. 高成本原材料TOP15排序
    ax3 = axes[1, 0]
    material_cost = df.groupby('原材料名称').agg({
        '总成本': 'sum',
        '品类': 'first'
    }).sort_values('总成本', ascending=True).tail(15)

    # 根据品类设置颜色
    color_map = {'主料': '#FF6B6B', '辅料': '#4ECDC4', '包装材料': '#45B7D1'}
    bar_colors = [color_map[cat] for cat in material_cost['品类']]

    bars = ax3.barh(material_cost.index, material_cost['总成本'], color=bar_colors, edgecolor='white', height=0.7)
    ax3.set_title('高成本原材料TOP15（按总成本排序）', fontsize=16, fontweight='bold', pad=20)
    ax3.set_xlabel('总成本 (元)', fontsize=13)
    ax3.tick_params(axis='both', labelsize=11)

    # 添加数值标签
    for i, (bar, cost) in enumerate(zip(bars, material_cost['总成本'])):
        ax3.text(cost + max(material_cost['总成本'])*0.01, bar.get_y() + bar.get_height()/2.,
                f'¥{cost:,.0f}',
                ha='left', va='center', fontsize=10)

    # 添加图例
    legend_patches = [mpatches.Patch(color=color, label=cat) for cat, color in color_map.items()]
    ax3.legend(handles=legend_patches, loc='lower right', fontsize=11)

    ax3.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax3.set_axisbelow(True)

    # 4. 品类成本箱线图（展示分布差异）
    ax4 = axes[1, 1]
    categories = ['主料', '辅料', '包装材料']
    cost_data = [df[df['品类'] == cat]['总成本'].values for cat in categories]

    bp = ax4.boxplot(cost_data, labels=categories, patch_artist=True)
    colors_box = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    for patch, color in zip(bp['boxes'], colors_box):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax4.set_title('各品类成本分布箱线图', fontsize=16, fontweight='bold', pad=20)
    ax4.set_ylabel('总成本 (元)', fontsize=13)
    ax4.set_xlabel('品类', fontsize=13)
    ax4.tick_params(axis='both', labelsize=11)
    ax4.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax4.set_axisbelow(True)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    return fig


# ==========================================
# 第三部分：损耗率高低可视化
# ==========================================

def plot_loss_rate_analysis(df):
    """
    第二维度：损耗率高低可视化
    - 不同原材料损耗率对比
    - 不同品类损耗率对比
    - 不同采购批次损耗率趋势
    """
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle('第二维度：损耗率高低可视化', fontsize=20, fontweight='bold', y=0.98)
    plt.subplots_adjust(hspace=0.35, wspace=0.3)

    # 1. 高损耗率原材料TOP15
    ax1 = axes[0, 0]
    material_loss = df.groupby('原材料名称').agg({
        '损耗率': 'mean',
        '品类': 'first'
    }).sort_values('损耗率', ascending=True).tail(15)

    color_map = {'主料': '#FF6B6B', '辅料': '#4ECDC4', '包装材料': '#45B7D1'}
    bar_colors = [color_map[cat] for cat in material_loss['品类']]

    bars = ax1.barh(material_loss.index, material_loss['损耗率'], color=bar_colors, edgecolor='white', height=0.7)
    ax1.set_title('高损耗率原材料TOP15', fontsize=16, fontweight='bold', pad=20)
    ax1.set_xlabel('平均损耗率 (%)', fontsize=13)
    ax1.tick_params(axis='both', labelsize=11)

    # 添加数值标签
    for bar, rate in zip(bars, material_loss['损耗率']):
        ax1.text(rate + 0.3, bar.get_y() + bar.get_height()/2.,
                f'{rate:.1f}%',
                ha='left', va='center', fontsize=10)

    # 添加警戒线
    ax1.axvline(x=5, color='orange', linestyle='--', linewidth=2, label='警戒线(5%)')
    ax1.axvline(x=8, color='red', linestyle='--', linewidth=2, label='高风险线(8%)')
    ax1.legend(loc='lower right', fontsize=10)

    # 2. 品类平均损耗率对比
    ax2 = axes[0, 1]
    category_loss = df.groupby('品类')['损耗率'].mean().sort_values(ascending=False)
    colors_bar = ['#FF6B6B', '#4ECDC4', '#45B7D1']

    bars = ax2.bar(category_loss.index, category_loss.values, color=colors_bar, edgecolor='white', linewidth=2)
    ax2.set_title('各品类平均损耗率对比', fontsize=16, fontweight='bold', pad=20)
    ax2.set_ylabel('平均损耗率 (%)', fontsize=13)
    ax2.set_xlabel('品类', fontsize=13)
    ax2.tick_params(axis='both', labelsize=11)

    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}%',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    # 添加警戒线
    ax2.axhline(y=5, color='orange', linestyle='--', linewidth=2, label='警戒线(5%)')
    ax2.legend(loc='upper right', fontsize=11)
    ax2.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax2.set_axisbelow(True)

    # 3. 采购批次损耗率趋势
    ax3 = axes[1, 0]
    batch_loss = df.groupby(['采购批次', '品类'])['损耗率'].mean().unstack()

    for i, category in enumerate(batch_loss.columns):
        ax3.plot(batch_loss.index, batch_loss[category], marker='o', linewidth=2.5,
                markersize=8, label=category, color=colors_bar[i])

    ax3.set_title('各品类损耗率月度趋势', fontsize=16, fontweight='bold', pad=20)
    ax3.set_ylabel('平均损耗率 (%)', fontsize=13)
    ax3.set_xlabel('采购批次', fontsize=13)
    ax3.legend(loc='best', fontsize=11)
    ax3.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax3.set_axisbelow(True)
    ax3.tick_params(axis='both', labelsize=11)

    # 4. 损耗率分布直方图
    ax4 = axes[1, 1]
    bins = [0, 2, 4, 6, 8, 10, 15]
    labels = ['0-2%', '2-4%', '4-6%', '6-8%', '8-10%', '10%+']

    df['损耗率区间'] = pd.cut(df['损耗率'], bins=bins, labels=labels, include_lowest=True)
    loss_distribution = df['损耗率区间'].value_counts().sort_index()

    bars = ax4.bar(loss_distribution.index, loss_distribution.values,
                   color=['#2ECC71', '#27AE60', '#F1C40F', '#E67E22', '#E74C3C', '#C0392B'],
                   edgecolor='white', linewidth=2)
    ax4.set_title('损耗率分布区间统计', fontsize=16, fontweight='bold', pad=20)
    ax4.set_ylabel('原材料批次数量', fontsize=13)
    ax4.set_xlabel('损耗率区间', fontsize=13)
    ax4.tick_params(axis='both', labelsize=11)

    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax4.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax4.set_axisbelow(True)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    return fig


# ==========================================
# 第四部分：损耗原因对成本的影响可视化
# ==========================================

def plot_loss_impact_analysis(df):
    """
    第三维度：损耗原因对成本的影响可视化
    - 不同损耗原因的成本损耗金额
    - 损耗原因与品类的关联热力图
    - 损耗原因与总成本的关联分析
    """
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle('第三维度：损耗原因对成本的影响可视化', fontsize=20, fontweight='bold', y=0.98)
    plt.subplots_adjust(hspace=0.35, wspace=0.3)

    # 1. 各损耗原因的成本损耗金额
    ax1 = axes[0, 0]
    reason_loss = df.groupby('损耗原因').agg({
        '损耗成本': 'sum',
        '总成本': 'sum'
    }).sort_values('损耗成本', ascending=False)

    reason_loss['损耗占比'] = reason_loss['损耗成本'] / reason_loss['总成本'] * 100

    bars = ax1.bar(reason_loss.index, reason_loss['损耗成本'],
                   color=['#E74C3C', '#3498DB', '#F39C12'], edgecolor='white', linewidth=2)
    ax1.set_title('各损耗原因导致的成本损耗金额', fontsize=16, fontweight='bold', pad=20)
    ax1.set_ylabel('损耗成本 (元)', fontsize=13)
    ax1.set_xlabel('损耗原因', fontsize=13)
    ax1.tick_params(axis='both', labelsize=11)

    # 添加数值标签
    for bar, cost in zip(bars, reason_loss['损耗成本']):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                f'¥{cost:,.0f}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax1.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax1.set_axisbelow(True)

    # 2. 损耗原因与品类的关联热力图
    ax2 = axes[0, 1]
    heatmap_data = df.pivot_table(
        values='损耗成本',
        index='损耗原因',
        columns='品类',
        aggfunc='sum'
    ).fillna(0)

    im = ax2.imshow(heatmap_data.values, cmap='Reds', aspect='auto')
    ax2.set_xticks(range(len(heatmap_data.columns)))
    ax2.set_yticks(range(len(heatmap_data.index)))
    ax2.set_xticklabels(heatmap_data.columns, fontsize=12)
    ax2.set_yticklabels(heatmap_data.index, fontsize=12)

    # 添加数值标签
    for i in range(len(heatmap_data.index)):
        for j in range(len(heatmap_data.columns)):
            text = ax2.text(j, i, f'¥{heatmap_data.values[i, j]:,.0f}',
                           ha="center", va="center", color="white" if heatmap_data.values[i, j] > heatmap_data.values.max()/2 else "black",
                           fontsize=11, fontweight='bold')

    ax2.set_title('损耗原因与品类关联热力图（损耗成本）', fontsize=16, fontweight='bold', pad=20)
    plt.colorbar(im, ax=ax2, label='损耗成本 (元)', shrink=0.8)

    # 3. 各损耗原因在不同品类的占比
    ax3 = axes[1, 0]
    reason_category = df.groupby(['损耗原因', '品类'])['损耗成本'].sum().unstack().fillna(0)
    reason_category_pct = reason_category.div(reason_category.sum(axis=1), axis=0) * 100

    x = np.arange(len(reason_category.index))
    width = 0.25

    bars1 = ax3.bar(x - width, reason_category_pct['主料'], width, label='主料', color='#FF6B6B')
    bars2 = ax3.bar(x, reason_category_pct['辅料'], width, label='辅料', color='#4ECDC4')
    bars3 = ax3.bar(x + width, reason_category_pct['包装材料'], width, label='包装材料', color='#45B7D1')

    ax3.set_title('各损耗原因的品类成本占比分布', fontsize=16, fontweight='bold', pad=20)
    ax3.set_ylabel('占比 (%)', fontsize=13)
    ax3.set_xlabel('损耗原因', fontsize=13)
    ax3.set_xticks(x)
    ax3.set_xticklabels(reason_category.index, fontsize=12)
    ax3.legend(loc='upper right', fontsize=11)
    ax3.tick_params(axis='y', labelsize=11)

    # 添加数值标签
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            if height > 5:  # 只显示较大的值
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}%',
                        ha='center', va='bottom', fontsize=10)

    ax3.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax3.set_axisbelow(True)

    # 4. 损耗原因影响权重（饼图）
    ax4 = axes[1, 1]
    loss_by_reason = df.groupby('损耗原因')['损耗成本'].sum().sort_values(ascending=False)

    colors_reason = ['#E74C3C', '#3498DB', '#F39C12']
    wedges, texts, autotexts = ax4.pie(
        loss_by_reason.values,
        labels=loss_by_reason.index,
        autopct='%1.1f%%',
        colors=colors_reason,
        explode=[0.03, 0.03, 0.03],
        shadow=True,
        startangle=90
    )

    ax4.set_title('损耗原因影响权重分布', fontsize=16, fontweight='bold', pad=20)

    for autotext in autotexts:
        autotext.set_fontsize(12)
        autotext.set_fontweight('bold')

    # 添加图例
    total_loss = loss_by_reason.sum()
    legend_labels = [f'{reason}: ¥{cost:,.0f} ({cost/total_loss*100:.1f}%)'
                     for reason, cost in loss_by_reason.items()]
    ax4.legend(wedges, legend_labels, title="损耗成本明细", loc="center left",
               bbox_to_anchor=(1.05, 0.5), fontsize=11, title_fontsize=12)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    return fig


# ==========================================
# 第五部分：综合关联分析可视化
# ==========================================

def plot_comprehensive_analysis(df):
    """
    综合关联分析：成本与损耗率的关联
    - 散点图：成本 vs 损耗率
    - 气泡图：成本、损耗率、损耗成本三维关联
    - 高成本高损耗核心数据标注
    """
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle('综合关联分析：成本与损耗率关联可视化', fontsize=20, fontweight='bold', y=0.98)
    plt.subplots_adjust(hspace=0.35, wspace=0.3)

    # 计算每个原材料的汇总数据
    material_summary = df.groupby('原材料名称').agg({
        '总成本': 'sum',
        '损耗率': 'mean',
        '损耗成本': 'sum',
        '品类': 'first'
    }).reset_index()

    # 1. 成本 vs 损耗率散点图
    ax1 = axes[0, 0]
    color_map = {'主料': '#FF6B6B', '辅料': '#4ECDC4', '包装材料': '#45B7D1'}

    for category in material_summary['品类'].unique():
        data = material_summary[material_summary['品类'] == category]
        ax1.scatter(data['总成本'], data['损耗率'],
                   s=100, alpha=0.7, label=category,
                   color=color_map[category], edgecolors='white', linewidth=1.5)

    # 添加象限分割线
    median_cost = material_summary['总成本'].median()
    median_loss = material_summary['损耗率'].median()
    ax1.axhline(y=median_loss, color='gray', linestyle='--', alpha=0.5)
    ax1.axvline(x=median_cost, color='gray', linestyle='--', alpha=0.5)

    # 标注高成本高损耗点
    high_cost_high_loss = material_summary[
        (material_summary['总成本'] > material_summary['总成本'].quantile(0.8)) &
        (material_summary['损耗率'] > material_summary['损耗率'].quantile(0.8))
    ]

    for _, row in high_cost_high_loss.iterrows():
        ax1.annotate(row['原材料名称'],
                    (row['总成本'], row['损耗率']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

    ax1.set_title('成本与损耗率关联散点图', fontsize=16, fontweight='bold', pad=20)
    ax1.set_xlabel('总成本 (元)', fontsize=13)
    ax1.set_ylabel('平均损耗率 (%)', fontsize=13)
    ax1.legend(loc='upper right', fontsize=11)
    ax1.tick_params(axis='both', labelsize=11)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # 添加象限标签
    ax1.text(0.95, 0.95, '高成本\n高损耗\n(重点关注)', transform=ax1.transAxes,
            fontsize=11, ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='red', alpha=0.3))
    ax1.text(0.05, 0.95, '低成本\n高损耗', transform=ax1.transAxes,
            fontsize=11, ha='left', va='top',
            bbox=dict(boxstyle='round', facecolor='orange', alpha=0.3))

    # 2. 气泡图：成本、损耗率、损耗成本
    ax2 = axes[0, 1]

    for category in material_summary['品类'].unique():
        data = material_summary[material_summary['品类'] == category]
        scatter = ax2.scatter(data['总成本'], data['损耗率'],
                             s=data['损耗成本']*2,  # 气泡大小表示损耗成本
                             alpha=0.6, label=category,
                             color=color_map[category], edgecolors='white', linewidth=1.5)

    ax2.set_title('成本-损耗率-损耗成本三维关联气泡图\n(气泡大小=损耗成本)', fontsize=16, fontweight='bold', pad=20)
    ax2.set_xlabel('总成本 (元)', fontsize=13)
    ax2.set_ylabel('平均损耗率 (%)', fontsize=13)
    ax2.legend(loc='upper right', fontsize=11)
    ax2.tick_params(axis='both', labelsize=11)
    ax2.grid(True, linestyle='--', alpha=0.5)

    # 3. 高成本高损耗核心数据表格
    ax3 = axes[1, 0]
    ax3.axis('off')

    # 筛选高成本高损耗数据
    priority_materials = material_summary[
        (material_summary['总成本'] > material_summary['总成本'].quantile(0.7)) |
        (material_summary['损耗率'] > material_summary['损耗率'].quantile(0.7))
    ].sort_values('损耗成本', ascending=False).head(10)

    table_data = []
    for _, row in priority_materials.iterrows():
        table_data.append([
            row['原材料名称'],
            row['品类'],
            f"¥{row['总成本']:,.0f}",
            f"{row['损耗率']:.2f}%",
            f"¥{row['损耗成本']:,.0f}"
        ])

    table = ax3.table(
        cellText=table_data,
        colLabels=['原材料名称', '品类', '总成本', '损耗率', '损耗成本'],
        cellLoc='center',
        loc='center',
        colWidths=[0.25, 0.15, 0.2, 0.15, 0.2]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.3, 2.2)

    # 设置表头样式
    for i in range(5):
        table[(0, i)].set_facecolor('#3498DB')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # 设置行颜色
    for i in range(1, len(table_data) + 1):
        category = table_data[i-1][1]
        if category == '主料':
            color = '#FFE5E5'
        elif category == '辅料':
            color = '#E5F7F5'
        else:
            color = '#E5F3F7'
        for j in range(5):
            table[(i, j)].set_facecolor(color)

    ax3.set_title('高成本/高损耗重点原材料TOP10', fontsize=16, fontweight='bold', pad=25)

    # 4. 成本节约潜力分析
    ax4 = axes[1, 1]

    # 计算如果损耗率降低50%可节约的成本
    material_summary['潜在节约'] = material_summary['损耗成本'] * 0.5
    top_savings = material_summary.nlargest(10, '潜在节约')

    bars = ax4.barh(top_savings['原材料名称'], top_savings['潜在节约'],
                    color='#27AE60', edgecolor='white', height=0.7)
    ax4.set_title('损耗管控优化潜在节约成本TOP10\n(假设损耗率降低50%)', fontsize=16, fontweight='bold', pad=20)
    ax4.set_xlabel('潜在节约成本 (元)', fontsize=13)
    ax4.tick_params(axis='both', labelsize=11)

    # 添加数值标签
    for bar, saving in zip(bars, top_savings['潜在节约']):
        ax4.text(saving + max(top_savings['潜在节约'])*0.01,
                bar.get_y() + bar.get_height()/2.,
                f'¥{saving:,.0f}',
                ha='left', va='center', fontsize=10)

    ax4.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax4.set_axisbelow(True)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    return fig


# ==========================================
# 主程序
# ==========================================

def main():
    """主程序：生成数据并创建所有可视化图表"""

    print("=" * 60)
    print("原材料成本与损耗率关联分析可视化方案")
    print("=" * 60)

    # 1. 生成数据
    print("\n[1/5] 正在生成原材料数据集...")
    df = generate_material_data()
    print(f"✓ 已生成 {len(df)} 条数据记录")
    print(f"  - 原材料种类: {df['原材料名称'].nunique()}")
    print(f"  - 数据时间跨度: {df['采购批次'].min()} 至 {df['采购批次'].max()}")

    # 保存数据
    df.to_csv('material_data.csv', index=False, encoding='utf-8-sig')
    print("✓ 数据已保存至 material_data.csv")

    # 显示数据概览
    print("\n数据概览:")
    print(df.head(10).to_string())
    print(f"\n数据统计:")
    print(df.groupby('品类').agg({
        '总成本': ['sum', 'mean'],
        '损耗率': 'mean',
        '损耗成本': 'sum'
    }).round(2))

    # 2. 创建可视化图表
    print("\n[2/5] 正在生成成本分布可视化...")
    fig1 = plot_cost_distribution(df)
    fig1.savefig('01_成本分布可视化.png', dpi=150, bbox_inches='tight', facecolor='white')
    print("✓ 已保存: 01_成本分布可视化.png")

    print("\n[3/5] 正在生成损耗率可视化...")
    fig2 = plot_loss_rate_analysis(df)
    fig2.savefig('02_损耗率可视化.png', dpi=150, bbox_inches='tight', facecolor='white')
    print("✓ 已保存: 02_损耗率可视化.png")

    print("\n[4/5] 正在生成损耗原因影响可视化...")
    fig3 = plot_loss_impact_analysis(df)
    fig3.savefig('03_损耗原因影响可视化.png', dpi=150, bbox_inches='tight', facecolor='white')
    print("✓ 已保存: 03_损耗原因影响可视化.png")

    print("\n[5/5] 正在生成综合关联分析...")
    fig4 = plot_comprehensive_analysis(df)
    fig4.savefig('04_综合关联分析.png', dpi=150, bbox_inches='tight', facecolor='white')
    print("✓ 已保存: 04_综合关联分析.png")

    # 显示图表
    plt.show()

    print("\n" + "=" * 60)
    print("可视化方案生成完成！")
    print("=" * 60)
    print("\n生成的文件:")
    print("  1. material_data.csv - 原材料数据集")
    print("  2. 01_成本分布可视化.png - 第一维度图表")
    print("  3. 02_损耗率可视化.png - 第二维度图表")
    print("  4. 03_损耗原因影响可视化.png - 第三维度图表")
    print("  5. 04_综合关联分析.png - 综合关联分析图表")

    return df


if __name__ == "__main__":
    df = main()
