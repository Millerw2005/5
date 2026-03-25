"""
商品销售数据分析工具
功能：生成模拟销售数据、销量排名分析、数据可视化及分析报告
作者：AI Assistant
版本：2.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
from matplotlib import font_manager

# ======================
# 配置常量区（集中管理所有配置）
# ======================
CONFIG = {
    'random_seed': 42,
    'n_products': 100,
    'top_n': 10,
    'figure_size': (24, 18),
    'figure_dpi': 120,
    'save_dpi': 150,
    'colors': [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ],
    'categories': ['电子产品', '服装鞋帽', '食品饮料', '家居用品', '美妆护肤', '运动户外'],
    'materials': ['塑料', '金属', '棉麻', '丝绸', '真皮', '合成材料', '玻璃', '陶瓷'],
    'specs': ['S', 'M', 'L', 'XL', 'XXL', '500ml', '1L', '2L', '5kg', '10kg'],
    'compare_metrics': ['曝光量', '点击率', '转化率'],
    'file_names': {
        'report': 'sales_analysis_report.md',
        'data': 'sales_data_analysis.csv',
        'chart': 'sales_analysis_dashboard.png'
    }
}

# ======================
# 字体配置模块
# ======================
def setup_chinese_font():
    """配置中文字体，解决图表乱码问题"""
    font_path = None
    
    # 查找系统中的中文字体
    for font in font_manager.findSystemFonts(fontpaths=None, fontext='ttf'):
        if any(keyword in font.lower() for keyword in ['msyh', 'yahei', 'simhei', 'pingfang', 'higuysong']):
            font_path = font
            break
    
    # 创建字体属性对象
    if font_path:
        font_prop = fm.FontProperties(fname=font_path, size=10)
        title_font_prop = fm.FontProperties(fname=font_path, size=14, weight='bold')
        label_font_prop = fm.FontProperties(fname=font_path, size=12)
    else:
        # fallback方案
        font_family = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
        font_prop = fm.FontProperties(family=font_family, size=10)
        title_font_prop = fm.FontProperties(family=font_family, size=14, weight='bold')
        label_font_prop = fm.FontProperties(family=font_family, size=12)
    
    # 全局matplotlib配置
    plt.rcParams.update({
        'figure.dpi': CONFIG['figure_dpi'],
        'axes.unicode_minus': False,
        'font.sans-serif': ['Microsoft YaHei', 'SimHei', 'DejaVu Sans'],
        'font.family': 'sans-serif',
    })
    
    return font_prop, title_font_prop, label_font_prop

# ======================
# 数据生成模块
# ======================
def generate_sales_data():
    """生成模拟销售数据"""
    np.random.seed(CONFIG['random_seed'])
    n = CONFIG['n_products']
    
    # 使用向量化操作替代循环，提升性能
    product_ids = [f'P{i:03d}' for i in range(1, n + 1)]
    product_names = [f'商品_{i}' for i in range(1, n + 1)]
    
    # 构建DataFrame
    df = pd.DataFrame({
        '商品ID': product_ids,
        '商品名称': product_names,
        '类目': np.random.choice(CONFIG['categories'], n),
        '价格': np.random.uniform(10, 5000, n).round(2),
        '规格': np.random.choice(CONFIG['specs'], n),
        '材质': np.random.choice(CONFIG['materials'], n),
        '上架时长': np.random.randint(1, 365, n),
        '总销量': np.random.lognormal(mean=6, sigma=1.5, size=n).astype(int),
        '促销力度': np.random.uniform(0, 0.5, n).round(2),
        '优惠券使用率': np.random.uniform(0, 0.4, n).round(2),
        '曝光量': np.random.randint(1000, 100000, n),
        '点击率': np.random.uniform(0.01, 0.15, n).round(4),
        '转化率': np.random.uniform(0.01, 0.1, n).round(4),
        '收藏加购率': np.random.uniform(0.02, 0.2, n).round(4),
        '评分': np.random.uniform(3.0, 5.0, n).round(1),
        '评价数': np.random.randint(10, 5000, n)
    })
    
    # 为爆款和滞销商品添加特征
    df = _add_sales_features(df)
    
    return df

def _add_sales_features(df):
    """为热销/滞销商品添加特征"""
    top_idx = df['总销量'].nlargest(CONFIG['top_n']).index
    bottom_idx = df['总销量'].nsmallest(CONFIG['top_n']).index
    
    # 使用.loc批量更新，性能更好
    df.loc[top_idx, '评分'] = df.loc[top_idx, '评分'].add(0.5).clip(upper=5.0)
    df.loc[top_idx, '转化率'] = df.loc[top_idx, '转化率'].add(0.03).clip(upper=0.15)
    df.loc[top_idx, '促销力度'] = df.loc[top_idx, '促销力度'].add(0.15).clip(upper=0.6)
    
    df.loc[bottom_idx, '评分'] = df.loc[bottom_idx, '评分'].sub(0.5).clip(lower=3.0)
    df.loc[bottom_idx, '转化率'] = df.loc[bottom_idx, '转化率'].sub(0.02).clip(lower=0.01)
    
    return df

def generate_trend_data():
    """生成TOP3商品近30天销量趋势数据"""
    return np.random.randint(50, 300, size=(3, 30))

# ======================
# 数据分析模块
# ======================
def analyze_sales_data(df):
    """执行销售数据分析"""
    df_sorted = df.sort_values('总销量', ascending=False).reset_index(drop=True)
    total_sales = df['总销量'].sum()
    
    # 只计算一次nlargest，避免重复计算
    top10 = df_sorted.head(CONFIG['top_n']).copy()
    bottom10 = df_sorted.tail(CONFIG['top_n']).copy()
    
    # 批量计算统计指标
    stats = {
        'df_sorted': df_sorted,
        'total_sales': total_sales,
        'top10': top10,
        'bottom10': bottom10,
        'top10_sales': top10['总销量'].sum(),
        'top10_ratio': top10['总销量'].sum() / total_sales,
        'median_sales': df['总销量'].median(),
        'median_product': df_sorted.iloc[len(df_sorted) // 2],
        'sales_std': df['总销量'].std(),
        'sales_mean': df['总销量'].mean(),
        'cv': df['总销量'].std() / df['总销量'].mean(),
        'category_metrics': _calculate_category_metrics(df)
    }
    
    return stats

def _calculate_category_metrics(df):
    """计算类目统计指标（避免重复groupby）"""
    return df.groupby('类目').agg({
        '总销量': 'sum',
        '转化率': 'mean',
        '点击率': 'mean'
    }).reset_index().assign(
        总销量标准化=lambda x: x['总销量'] / x['总销量'].max(),
        转化率标准化=lambda x: x['转化率'] / x['转化率'].max()
    )

# ======================
# 数据可视化模块
# ======================
def create_visualizations(stats, trend_data, fonts):
    """创建所有可视化图表"""
    font_prop, title_font_prop, label_font_prop = fonts
    fig = plt.figure(figsize=CONFIG['figure_size'])
    
    # 使用字典存储子图，便于管理
    axes = {
        'bar_top10': plt.subplot(3, 2, 1),
        'pie_ratio': plt.subplot(3, 2, 2),
        'scatter_price': plt.subplot(3, 2, 3),
        'line_trend': plt.subplot(3, 2, 4),
        'heatmap_category': plt.subplot(3, 2, 5),
        'bar_compare': plt.subplot(3, 2, 6)
    }
    
    # 绘制各类图表
    _plot_top10_bar(axes['bar_top10'], stats['top10'], title_font_prop, label_font_prop, font_prop)
    _plot_sales_pie(axes['pie_ratio'], stats, title_font_prop, font_prop)
    _plot_price_correlation(axes['scatter_price'], stats['df_sorted'], title_font_prop, label_font_prop, font_prop)
    _plot_sales_trend(axes['line_trend'], stats['top10'], trend_data, title_font_prop, label_font_prop, font_prop)
    _plot_category_heatmap(axes['heatmap_category'], stats['category_metrics'], title_font_prop, font_prop)
    _plot_hot_cold_compare(axes['bar_compare'], stats, title_font_prop, label_font_prop, font_prop)
    
    # 统一调整布局并保存
    plt.tight_layout()
    plt.savefig(CONFIG['file_names']['chart'], dpi=CONFIG['save_dpi'], bbox_inches='tight')
    plt.close()

def _plot_top10_bar(ax, top10, title_font, label_font, tick_font):
    """绘制TOP10商品销量柱状图"""
    bars = ax.bar(top10['商品名称'], top10['总销量'], color=CONFIG['colors'][:10])
    ax.set_title('TOP10商品销量排名', fontproperties=title_font, pad=20)
    ax.set_xlabel('商品名称', fontproperties=label_font)
    ax.set_ylabel('销量', fontproperties=label_font)
    ax.tick_params(axis='x', rotation=45)
    
    # 设置刻度字体
    plt.setp(ax.get_xticklabels(), fontproperties=tick_font, ha='right')
    plt.setp(ax.get_yticklabels(), fontproperties=tick_font)
    
    # 添加数值标签
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f'{int(bar.get_height())}', ha='center', va='bottom', fontproperties=tick_font)

def _plot_sales_pie(ax, stats, title_font, text_font):
    """绘制销量占比饼图"""
    other_sales = stats['total_sales'] - stats['top10_sales']
    pie_sizes = list(stats['top10']['总销量']) + [other_sales]
    pie_labels = list(stats['top10']['商品名称']) + ['其他商品']
    
    wedges, texts, autotexts = ax.pie(
        pie_sizes, labels=pie_labels, autopct='%1.1f%%',
        colors=CONFIG['colors'][:10] + ['#f0f0f0']
    )
    
    ax.set_title(
        f'TOP10商品销量占总销量比例\n总销量: {stats["total_sales"]:,}',
        fontproperties=title_font, pad=20
    )
    
    # 设置字体
    for text in texts:
        text.set_fontproperties(text_font)
    for autotext in autotexts:
        autotext.set_fontproperties(text_font)

def _plot_price_correlation(ax, df, title_font, label_font, tick_font):
    """绘制价格与销量相关性散点图"""
    ax.scatter(df['价格'], df['总销量'], alpha=0.6, c=CONFIG['colors'][0], s=50)
    ax.set_title('商品价格与销量相关性分析', fontproperties=title_font, pad=20)
    ax.set_xlabel('价格（元）', fontproperties=label_font)
    ax.set_ylabel('销量', fontproperties=label_font)
    ax.set_xscale('log')
    
    plt.setp(ax.get_xticklabels(), fontproperties=tick_font)
    plt.setp(ax.get_yticklabels(), fontproperties=tick_font)
    
    # 添加趋势线
    z = np.polyfit(np.log(df['价格']), df['总销量'], 1)
    p = np.poly1d(z)
    x_trend = np.logspace(1, 4, 100)
    ax.plot(x_trend, p(np.log(x_trend)), "r--", alpha=0.8)

def _plot_sales_trend(ax, top10, trend_data, title_font, label_font, tick_font):
    """绘制TOP3商品销量趋势折线图"""
    days = range(1, 31)
    for i in range(3):
        ax.plot(days, trend_data[i], label=f'{top10.iloc[i]["商品名称"]}',
                color=CONFIG['colors'][i], linewidth=2, marker='o', markersize=4)
    
    ax.set_title('TOP3爆款商品近30天销量趋势', fontproperties=title_font, pad=20)
    ax.set_xlabel('天数', fontproperties=label_font)
    ax.set_ylabel('日销量', fontproperties=label_font)
    ax.legend(prop=tick_font)
    ax.grid(True, alpha=0.3)
    
    plt.setp(ax.get_xticklabels(), fontproperties=tick_font)
    plt.setp(ax.get_yticklabels(), fontproperties=tick_font)

def _plot_category_heatmap(ax, category_metrics, title_font, tick_font):
    """绘制类目热力图"""
    heatmap_data = category_metrics[['类目', '总销量标准化', '转化率标准化']].set_index('类目')
    heatmap = sns.heatmap(heatmap_data, annot=True, cmap='YlOrRd', ax=ax, fmt='.2f')
    
    ax.set_title('不同类目商品的销量与转化率关联热力图', fontproperties=title_font, pad=20)
    ax.set_yticklabels(ax.get_yticklabels(), fontproperties=tick_font)
    ax.set_xticklabels(ax.get_xticklabels(), fontproperties=tick_font)
    
    for text in heatmap.texts:
        text.set_fontproperties(tick_font)

def _plot_hot_cold_compare(ax, stats, title_font, label_font, tick_font):
    """绘制爆款与滞销商品对比图"""
    hot_avg = stats['top10'][CONFIG['compare_metrics']].mean()
    cold_avg = stats['bottom10'][CONFIG['compare_metrics']].mean()
    
    x = np.arange(len(CONFIG['compare_metrics']))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, hot_avg, width, label='爆款商品', color=CONFIG['colors'][0])
    rects2 = ax.bar(x + width/2, cold_avg, width, label='滞销商品', color=CONFIG['colors'][3])
    
    ax.set_title('爆款与滞销商品运营数据对比', fontproperties=title_font, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(CONFIG['compare_metrics'], fontproperties=tick_font)
    ax.legend(prop=tick_font)
    ax.set_yscale('log')
    
    plt.setp(ax.get_yticklabels(), fontproperties=tick_font)
    
    # 添加数值标签的辅助函数
    def add_labels(rects, is_hot=True):
        for rect in rects:
            height = rect.get_height()
            if rect.get_x() > 0.5:
                label = f'{height:.2%}'
            else:
                label = f'{int(height):,}'
            ax.text(rect.get_x() + rect.get_width()/2, height, label,
                    ha='center', va='bottom', fontproperties=tick_font)
    
    add_labels(rects1)
    add_labels(rects2)

# ======================
# 报告生成模块
# ======================
def generate_report(stats):
    """生成Markdown分析报告"""
    top10_stats = stats['top10'].agg({
        '价格': 'mean',
        '评分': 'mean',
        '转化率': 'mean',
        '促销力度': 'mean'
    }).round(4)
    
    all_stats = stats['df_sorted'].agg({
        '价格': 'mean',
        '评分': 'mean',
        '转化率': 'mean',
        '促销力度': 'mean'
    }).round(4)
    
    # 优化类目排序
    category_dist = stats['top10']['类目'].value_counts().reindex(CONFIG['categories']).dropna()
    high_convert_category = stats['category_metrics'].sort_values('转化率', ascending=False).iloc[0]['类目']
    low_sales_category = stats['category_metrics'].sort_values('总销量', ascending=True).iloc[0]['类目']
    
    return f"""# 商品销售数据分析报告

## 一、销量排名概览

### 1.1 TOP10爆款商品
{stats['top10'][['商品ID', '商品名称', '类目', '价格', '总销量', '评分']].to_markdown(index=False, floatfmt='.2f')}

### 1.2 销量垫底10款商品
{stats['bottom10'][['商品ID', '商品名称', '类目', '价格', '总销量', '评分']].to_markdown(index=False, floatfmt='.2f')}

### 1.3 核心统计指标
| 指标 | 数值 |
|------|------|
| 商品总数 | {CONFIG['n_products']} |
| 总销量 | {stats['total_sales']:,} |
| TOP10商品销量占比 | {stats['top10_ratio']:.2%} |
| 销量中位数 | {stats['median_sales']:.0f} |
| 销量均值 | {stats['sales_mean']:.2f} |
| 销量标准差 | {stats['sales_std']:.2f} |
| 变异系数 | {stats['cv']:.2f} |

## 二、销量分布特征分析

**销量分布特征：{('集中分布' if stats['top10_ratio'] > 0.3 else '分散分布')}**
- TOP10商品贡献了总销量的 {stats['top10_ratio']:.2%}，销量头部{('集中效应明显' if stats['top10_ratio'] > 0.3 else '分布相对均匀')}
- 变异系数为 {stats['cv']:.2f}，表明销量离散程度{('较大' if stats['cv'] > 1 else '一般')}
- 中位数商品（{stats['median_product']['商品名称']}）销量为 {stats['median_product']['总销量']}，仅为TOP1商品销量的 {(stats['median_product']['总销量']/stats['top10'].iloc[0]['总销量']):.2%}

## 三、热销原因深度拆解

### 3.1 爆款商品共性特征
1. **价格策略**：TOP10商品均价 {top10_stats['价格']:.2f} 元，整体均价 {all_stats['价格']:.2f} 元，定价{('略高于' if top10_stats['价格'] > all_stats['价格'] else '低于')}整体水平
2. **用户评价**：平均评分 {top10_stats['评分']:.2f}，{('显著高于' if top10_stats['评分'] > all_stats['评分'] else '接近')}整体均值 {all_stats['评分']:.2f}
3. **运营效率**：平均转化率 {top10_stats['转化率']:.2%}，{('显著高于' if top10_stats['转化率'] > all_stats['转化率'] else '接近')}整体均值 {all_stats['转化率']:.2%}
4. **促销力度**：平均促销折扣 {top10_stats['促销力度']:.2%}，{('高于' if top10_stats['促销力度'] > all_stats['促销力度'] else '低于')}整体的 {all_stats['促销力度']:.2%}

### 3.2 类目分布
```
{category_dist.to_markdown(floatfmt='.0f')}
```

## 四、优劣商品对比分析

| 指标 | 爆款商品（TOP10） | 滞销商品（后10） | 差值 |
|------|----------------|----------------|------|
| 平均价格 | {stats['top10']['价格'].mean():.2f} | {stats['bottom10']['价格'].mean():.2f} | {stats['top10']['价格'].mean()-stats['bottom10']['价格'].mean():.2f} |
| 平均销量 | {stats['top10']['总销量'].mean():.0f} | {stats['bottom10']['总销量'].mean():.0f} | {stats['top10']['总销量'].mean()-stats['bottom10']['总销量'].mean():.0f} |
| 平均评分 | {stats['top10']['评分'].mean():.2f} | {stats['bottom10']['评分'].mean():.2f} | {stats['top10']['评分'].mean()-stats['bottom10']['评分'].mean():.2f} |
| 平均转化率 | {stats['top10']['转化率'].mean():.2%} | {stats['bottom10']['转化率'].mean():.2%} | {(stats['top10']['转化率'].mean()-stats['bottom10']['转化率'].mean())*100:.2f}pct |
| 平均曝光量 | {stats['top10']['曝光量'].mean():,.0f} | {stats['bottom10']['曝光量'].mean():,.0f} | {stats['top10']['曝光量'].mean()-stats['bottom10']['曝光量'].mean():,.0f} |

## 五、可落地优化建议

### 5.1 爆款商品维护策略
1. **库存保障**：确保TOP10商品（如{stats['top10'].iloc[0]['商品名称']}、{stats['top10'].iloc[1]['商品名称']}等）库存充足，避免断货影响销售
2. **价格稳定**：爆款商品价格敏感度高，建议维持现有价格策略，可适当增加捆绑销售
3. **口碑营销**：利用{stats['top10']['评分'].mean():.2f}分的高评分优势，开展用户晒单、好评返现等活动
4. **关联推荐**：在爆款商品页面推荐同类目或互补商品，提升客单价

### 5.2 滞销商品改进方案
1. **价格调整**：考虑适当降价（建议降幅10%-20%）或开展买一赠一、捆绑销售
2. **流量扶持**：增加滞销商品的曝光机会，可在首页推荐、商品详情页设置关联推荐
3. **产品优化**：分析差评原因（如果有），优化产品设计或升级换代
4. **清仓策略**：对长期滞销商品可设置清仓专区，快速回笼资金

### 5.3 类目运营建议
1. 🔥 **重点扶持高转化类目**：{high_convert_category}，该类目转化率表现最佳
2. ⚠️ **优化低销量类目**：{low_sales_category}，考虑调整选品策略或增加营销投入
3. 📊 **类目差异化策略**：针对不同类目制定差异化的营销和定价策略

### 5.4 数据驱动运营建议
1. **监控关键指标**：重点关注转化率、收藏加购率等核心运营指标
2. **A/B测试**：对价格、促销力度等变量进行A/B测试，找到最优解
3. **用户反馈闭环**：建立用户评价分析机制，及时发现并解决产品问题

## 六、数据可视化图表

已生成可视化分析仪表板：`{CONFIG['file_names']['chart']}`

图表内容包括：
1. 📊 TOP10商品销量排名柱状图（带数值标注）
2. 🥧 TOP10商品销量占比饼图（清晰展示头部集中度）
3. 📈 价格与销量相关性散点图（含趋势线分析）
4. 📉 TOP3商品近30天销量趋势折线图（洞察销售动态）
5. 🌡️ 类目销量与转化率关联热力图（发现高潜类目）
6. 🆚 爆款与滞销商品运营数据对比图（定位核心差距）
"""

def save_results(stats, report):
    """保存所有结果文件"""
    # 保存报告
    with open(CONFIG['file_names']['report'], 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 保存数据（按销量排序，增加可读性）
    stats['df_sorted'].to_csv(CONFIG['file_names']['data'], encoding='utf-8-sig', index=False)
    
    print("=" * 60)
    print("📊 商品销售数据分析完成！")
    print("=" * 60)
    print(f"📄 分析报告：{CONFIG['file_names']['report']}")
    print(f"📈 完整数据：{CONFIG['file_names']['data']}")
    print(f"🖼️ 可视化图表：{CONFIG['file_names']['chart']}")
    print("=" * 60)

# ======================
# 主执行函数
# ======================
def main():
    """主执行函数"""
    try:
        # 1. 配置字体
        fonts = setup_chinese_font()
        
        # 2. 生成数据
        df = generate_sales_data()
        trend_data = generate_trend_data()
        
        # 3. 数据分析
        stats = analyze_sales_data(df)
        
        # 4. 创建可视化
        create_visualizations(stats, trend_data, fonts)
        
        # 5. 生成报告
        report = generate_report(stats)
        
        # 6. 保存结果
        save_results(stats, report)
        
    except Exception as e:
        print(f"❌ 分析过程出现错误：{str(e)}")
        raise

if __name__ == "__main__":
    main()
