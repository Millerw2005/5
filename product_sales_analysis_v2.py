"""
商品销售数据全面分析系统 V2.0
优化版本：面向对象设计、性能优化、代码重构

优化点：
1. 采用面向对象设计，提高代码可维护性
2. 使用向量化运算替代循环，提升性能
3. 添加类型注解，增强代码可读性
4. 增加异常处理和日志记录
5. 优化可视化效果
6. 支持配置化参数
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, field
from pathlib import Path
import warnings
import logging
from functools import lru_cache

warnings.filterwarnings('ignore')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun', 'FangSong', 'KaiTi']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10


@dataclass
class AnalysisConfig:
    """分析配置类"""
    n_products: int = 150
    random_seed: int = 42
    top_n: int = 10
    bottom_n: int = 10
    output_dir: Path = field(default_factory=lambda: Path('.'))
    chart_dpi: int = 150
    chart_figsize: Tuple[int, int] = (18, 20)
    
    def __post_init__(self):
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)


@dataclass  
class SalesMetrics:
    """销售指标数据类"""
    total_sales: int
    top10_sales: int
    top10_ratio: float
    sales_std: float
    sales_cv: float
    sales_mean: float
    sales_median: float


class DataGenerator:
    """数据生成器类 - 负责生成模拟销售数据"""
    
    # 类常量定义
    CATEGORIES = ['数码电子', '服装配饰', '家居生活', '美妆护肤', '食品饮料', 
                  '运动户外', '母婴用品', '图书文具']
    MATERIALS = ['塑料', '金属', '棉质', '化纤', '玻璃', '木质', '硅胶', '混合材质']
    SPECS = ['标准版', '升级版', '豪华版', '迷你版', '家庭装', '便携装']
    SEASONS = ['春季', '夏季', '秋季', '冬季']
    
    CATEGORY_PREFIXES = {
        '数码电子': ['智能', '无线', '便携', '高清', '快充'],
        '服装配饰': ['时尚', '简约', '复古', '运动', '商务'],
        '家居生活': ['创意', '实用', '环保', '智能', '简约'],
        '美妆护肤': ['天然', '保湿', '美白', '抗衰', '清爽'],
        '食品饮料': ['有机', '健康', '美味', '新鲜', '进口'],
        '运动户外': ['专业', '轻便', '耐用', '透气', '防滑'],
        '母婴用品': ['安全', '舒适', '可爱', '益智', '环保'],
        '图书文具': ['经典', '实用', '创意', '便携', '精装']
    }
    
    CATEGORY_ITEMS = {
        '数码电子': ['蓝牙耳机', '充电宝', '数据线', '手机壳', '智能手表'],
        '服装配饰': ['T恤', '牛仔裤', '运动鞋', '背包', '围巾'],
        '家居生活': ['收纳盒', '台灯', '抱枕', '水杯', '厨具套装'],
        '美妆护肤': ['面膜', '洗面奶', '精华液', '口红', '防晒霜'],
        '食品饮料': ['坚果礼盒', '咖啡', '茶叶', '蜂蜜', '燕麦片'],
        '运动户外': ['瑜伽垫', '跳绳', '护膝', '运动水壶', '登山杖'],
        '母婴用品': ['奶瓶', '纸尿裤', '婴儿湿巾', '辅食机', '玩具'],
        '图书文具': ['笔记本', '签字笔', '便利贴', '小说', '绘本']
    }
    
    BASE_EXPOSURE = {
        '数码电子': 50000, '服装配饰': 80000, '家居生活': 60000,
        '美妆护肤': 70000, '食品饮料': 90000, '运动户外': 40000,
        '母婴用品': 45000, '图书文具': 35000
    }
    
    POSITIVE_KEYWORDS = ['质量好', '性价比高', '物流快', '包装精美', '服务态度好', 
                        '正品保障', '使用方便', '效果显著', '款式新颖', '材质优良']
    NEGATIVE_REASONS = ['物流慢', '与描述不符', '质量一般', '包装破损', '尺寸不合适',
                       '色差严重', '效果不好', '价格偏高', '售后服务差']
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.rng = np.random.default_rng(config.random_seed)
    
    def generate(self) -> pd.DataFrame:
        """生成完整的销售数据集"""
        logger.info(f"开始生成 {self.config.n_products} 条商品数据...")
        
        n = self.config.n_products
        
        # 生成基础属性 - 使用向量化操作
        data = pd.DataFrame({
            '商品ID': [f'P{str(i).zfill(4)}' for i in range(1, n + 1)],
            '类目': self.rng.choice(self.CATEGORIES, n),
            '价格': np.round(self.rng.uniform(19.9, 999.9, n), 2),
            '规格': self.rng.choice(self.SPECS, n),
            '材质': self.rng.choice(self.MATERIALS, n),
            '上架天数': self.rng.integers(30, 730, n),
        })
        
        # 生成商品名称
        data['商品名称'] = data['类目'].apply(self._generate_product_name)
        
        # 生成运营数据
        data = self._generate_operation_data(data)
        
        # 生成用户反馈数据
        data = self._generate_feedback_data(data)
        
        # 生成外部因素
        data = self._generate_external_factors(data)
        
        # 计算销量
        data = self._calculate_sales(data)
        
        logger.info(f"数据生成完成，共 {len(data)} 条记录")
        return data
    
    def _generate_product_name(self, category: str) -> str:
        """生成商品名称"""
        prefix = self.rng.choice(self.CATEGORY_PREFIXES[category])
        item = self.rng.choice(self.CATEGORY_ITEMS[category])
        return f'{prefix}{item}'
    
    def _generate_operation_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成运营数据 - 向量化实现"""
        # 曝光量
        data['曝光量'] = data['类目'].map(self.BASE_EXPOSURE) * self.rng.uniform(0.3, 2.0, len(data))
        data['曝光量'] = data['曝光量'].round().astype(int)
        
        # 点击率 - 与价格相关
        data['点击率'] = self.rng.beta(2, 8, len(data)) * 0.15 + 0.01
        data.loc[data['价格'] < 50, '点击率'] *= 1.3
        data.loc[data['价格'] > 500, '点击率'] *= 0.7
        data['点击率'] = data['点击率'].round(4)
        
        # 转化率
        data['转化率'] = self.rng.beta(3, 10, len(data)) * 0.08 + 0.005
        data['转化率'] = data['转化率'].round(4)
        
        # 收藏加购率
        data['收藏加购率'] = data['点击率'] * self.rng.uniform(0.3, 0.8, len(data))
        data['收藏加购率'] = data['收藏加购率'].round(4)
        
        # 促销力度
        promo_probs = [0.3, 0.25, 0.2, 0.15, 0.1]
        data['促销力度'] = self.rng.choice([0, 0.1, 0.2, 0.3, 0.5], len(data), p=promo_probs)
        
        # 优惠券使用占比
        data['优惠券使用占比'] = self.rng.beta(2, 5, len(data)) * 0.6
        data.loc[data['促销力度'] > 0, '优惠券使用占比'] *= 1.5
        data['优惠券使用占比'] = data['优惠券使用占比'].clip(0, 1).round(4)
        
        return data
    
    def _generate_feedback_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成用户反馈数据"""
        data['评价评分'] = np.clip(self.rng.normal(4.3, 0.6, len(data)), 1, 5).round(2)
        
        # 好评关键词
        data['好评关键词'] = [
            ', '.join(self.rng.choice(self.POSITIVE_KEYWORDS, size=self.rng.integers(2, 5), replace=False))
            for _ in range(len(data))
        ]
        
        # 差评原因
        data['差评原因'] = [
            ', '.join(self.rng.choice(self.NEGATIVE_REASONS, size=self.rng.integers(0, 3), replace=False))
            if self.rng.random() > 0.6 else '无'
            for _ in range(len(data))
        ]
        
        return data
    
    def _generate_external_factors(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成外部因素数据"""
        data['季节趋势'] = self.rng.choice(self.SEASONS, len(data))
        data['节日效应'] = self.rng.choice([0, 1], len(data), p=[0.7, 0.3])
        data['竞品动态'] = self.rng.choice(['竞争激烈', '竞争一般', '竞争较小'], len(data), p=[0.3, 0.5, 0.2])
        return data
    
    def _calculate_sales(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算销量 - 核心算法"""
        season_factor = data['季节趋势'].map({'春季': 1.0, '夏季': 1.1, '秋季': 1.0, '冬季': 0.9})
        promo_factor = 1 + data['促销力度'] * 0.5
        rating_factor = (data['评价评分'] / 5) ** 2
        holiday_factor = 1 + data['节日效应'] * 0.3
        
        # 基础销量计算
        base_sales = (data['曝光量'] * data['点击率'] * data['转化率'] * 1000 * 
                     season_factor * promo_factor * rating_factor * holiday_factor)
        
        # 添加对数正态分布的随机波动
        data['销量'] = (base_sales * self.rng.lognormal(0, 0.5, len(data))).round().astype(int)
        data['销量'] = data['销量'].clip(10, 50000)
        
        # 计算销售额
        data['销售额'] = (data['销量'] * data['价格'] * (1 - data['促销力度'])).round(2)
        
        return data


class SalesAnalyzer:
    """销售分析器类 - 负责数据分析"""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
    
    def analyze(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, SalesMetrics, Dict]:
        """执行完整分析"""
        logger.info("开始数据分析...")
        
        # 销量排名
        ranked_data = self._rank_by_sales(data)
        
        # 提取TOP和BOTTOM
        top_n = ranked_data.head(self.config.top_n)
        bottom_n = ranked_data.tail(self.config.bottom_n).sort_values('销量')
        
        # 计算核心指标
        metrics = self._calculate_metrics(data, top_n)
        
        # 深度分析
        analysis_results = {
            'top_n': top_n,
            'bottom_n': bottom_n,
            'median_product': ranked_data.iloc[len(ranked_data) // 2],
            'category_distribution': self._analyze_category_distribution(top_n),
            'price_analysis': self._analyze_price(data, top_n, bottom_n),
            'operation_metrics': self._analyze_operation_metrics(data, top_n, bottom_n),
            'feedback_analysis': self._analyze_feedback(data, top_n, bottom_n),
            'external_factors': self._analyze_external_factors(data)
        }
        
        logger.info("数据分析完成")
        return ranked_data, metrics, analysis_results
    
    def _rank_by_sales(self, data: pd.DataFrame) -> pd.DataFrame:
        """按销量排序"""
        ranked = data.sort_values('销量', ascending=False).reset_index(drop=True)
        ranked['排名'] = range(1, len(ranked) + 1)
        return ranked
    
    def _calculate_metrics(self, data: pd.DataFrame, top_n: pd.DataFrame) -> SalesMetrics:
        """计算核心销售指标"""
        total_sales = data['销量'].sum()
        top_n_sales = top_n['销量'].sum()
        
        return SalesMetrics(
            total_sales=total_sales,
            top10_sales=top_n_sales,
            top10_ratio=top_n_sales / total_sales * 100,
            sales_std=data['销量'].std(),
            sales_cv=data['销量'].std() / data['销量'].mean() * 100,
            sales_mean=data['销量'].mean(),
            sales_median=data['销量'].median()
        )
    
    def _analyze_category_distribution(self, top_n: pd.DataFrame) -> pd.Series:
        """分析类目分布"""
        return top_n['类目'].value_counts()
    
    def _analyze_price(self, data: pd.DataFrame, top_n: pd.DataFrame, 
                       bottom_n: pd.DataFrame) -> Dict[str, float]:
        """分析价格特征"""
        return {
            'top_avg': top_n['价格'].mean(),
            'all_avg': data['价格'].mean(),
            'bottom_avg': bottom_n['价格'].mean()
        }
    
    def _analyze_operation_metrics(self, data: pd.DataFrame, top_n: pd.DataFrame,
                                   bottom_n: pd.DataFrame) -> pd.DataFrame:
        """分析运营指标对比"""
        metrics = ['曝光量', '点击率', '转化率', '促销力度', '优惠券使用占比']
        
        results = []
        for metric in metrics:
            top_avg = top_n[metric].mean()
            all_avg = data[metric].mean()
            bottom_avg = bottom_n[metric].mean()
            gap = top_avg / bottom_avg if bottom_avg > 0 else float('inf')
            
            results.append({
                '指标': metric,
                'TOP均值': top_avg,
                '全店均值': all_avg,
                '滞销均值': bottom_avg,
                '差距倍数': gap
            })
        
        return pd.DataFrame(results)
    
    def _analyze_feedback(self, data: pd.DataFrame, top_n: pd.DataFrame,
                          bottom_n: pd.DataFrame) -> Dict:
        """分析用户反馈"""
        # 好评关键词统计
        all_keywords = []
        for keywords in top_n['好评关键词']:
            all_keywords.extend([k.strip() for k in keywords.split(',')])
        keyword_counts = pd.Series(all_keywords).value_counts().head(5)
        
        return {
            'top_rating': top_n['评价评分'].mean(),
            'all_rating': data['评价评分'].mean(),
            'bottom_rating': bottom_n['评价评分'].mean(),
            'top_keywords': keyword_counts.to_dict()
        }
    
    def _analyze_external_factors(self, data: pd.DataFrame) -> Dict:
        """分析外部因素"""
        season_sales = data.groupby('季节趋势')['销量'].mean().sort_values(ascending=False)
        holiday_effect = data.groupby('节日效应')['销量'].mean()
        
        return {
            'season_sales': season_sales.to_dict(),
            'holiday_lift': (holiday_effect[1] / holiday_effect[0] - 1) * 100
        }


class Visualizer:
    """可视化类 - 负责图表生成"""
    
    COLORS = {
        'primary': '#2E86AB',
        'secondary': '#A23B72',
        'accent': '#F18F01',
        'success': '#C73E1D',
        'neutral': '#6B7280',
        'light': '#E5E7EB',
        'top10': ['#1a5276', '#2874a6', '#3498db', '#5dade2', '#85c1e9', 
                  '#aed6f1', '#d4e6f1', '#ebf5fb', '#f8f9f9', '#fdfefe']
    }
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
    
    def create_dashboard(self, data: pd.DataFrame, top_n: pd.DataFrame,
                         bottom_n: pd.DataFrame, metrics: SalesMetrics) -> plt.Figure:
        """创建完整的可视化仪表板"""
        logger.info("开始生成可视化图表...")
        
        plt.close('all')
        fig = plt.figure(figsize=self.config.chart_figsize)
        
        # 6个核心图表
        self._plot_top10_ranking(fig, top_n, 1)
        self._plot_sales_share(fig, top_n, metrics, 2)
        self._plot_price_correlation(fig, data, top_n, 3)
        self._plot_trend(fig, top_n, 4)
        self._plot_heatmap(fig, data, 5)
        self._plot_comparison(fig, top_n, bottom_n, 6)
        
        plt.tight_layout(pad=2.5)
        
        # 保存图表
        output_path = self.config.output_dir / 'product_sales_analysis.png'
        plt.savefig(output_path, dpi=self.config.chart_dpi, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        logger.info(f"图表已保存: {output_path}")
        
        return fig
    
    def _plot_top10_ranking(self, fig: plt.Figure, top_n: pd.DataFrame, position: int):
        """TOP10销量排名柱状图"""
        ax = fig.add_subplot(3, 2, position)
        
        bars = ax.barh(range(len(top_n)), top_n['销量'].values, 
                      color=self.COLORS['top10'])
        ax.set_yticks(range(len(top_n)))
        ax.set_yticklabels([f"{name[:8]}" for name in top_n['商品名称']], fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel('Sales (Units)', fontsize=11)
        ax.set_title('TOP10 Product Sales Ranking', fontsize=13, fontweight='bold', pad=15)
        
        # 添加数值标签
        for bar, sales in zip(bars, top_n['销量'].values):
            ax.text(sales + max(top_n['销量']) * 0.01, bar.get_y() + bar.get_height()/2,
                   f'{sales:,}', va='center', fontsize=9, fontweight='bold')
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    def _plot_sales_share(self, fig: plt.Figure, top_n: pd.DataFrame, 
                          metrics: SalesMetrics, position: int):
        """销量占比饼图"""
        ax = fig.add_subplot(3, 2, position)
        
        top_sales = top_n['销量'].sum()
        other_sales = metrics.total_sales - top_sales
        
        pie_data = list(top_n['销量'].values) + [other_sales]
        pie_labels = [f"#{i+1}" for i in range(len(top_n))] + ['Others']
        pie_colors = self.COLORS['top10'][:len(top_n)] + ['#E8E8E8']
        
        wedges, texts, autotexts = ax.pie(
            pie_data, labels=pie_labels, autopct='%1.1f%%',
            colors=pie_colors, startangle=90, textprops={'fontsize': 9}
        )
        ax.set_title(f'TOP10 Sales Share\n(TOP10: {metrics.top10_ratio:.1f}% of Total)',
                    fontsize=13, fontweight='bold', pad=15)
    
    def _plot_price_correlation(self, fig: plt.Figure, data: pd.DataFrame,
                                top_n: pd.DataFrame, position: int):
        """价格与销量相关性散点图"""
        ax = fig.add_subplot(3, 2, position)
        
        categories = data['类目'].unique()
        cat_colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
        
        for i, cat in enumerate(categories):
            cat_data = data[data['类目'] == cat]
            ax.scatter(cat_data['价格'], cat_data['销量'], alpha=0.6, s=60,
                      c=[cat_colors[i]], label=cat[:4], edgecolors='white', linewidth=0.5)
        
        ax.scatter(top_n['价格'], top_n['销量'], s=180, c='red', marker='*',
                  label='TOP10', edgecolors='darkred', linewidth=1.5, zorder=5)
        
        ax.set_xlabel('Price (CNY)', fontsize=11)
        ax.set_ylabel('Sales (Units)', fontsize=11)
        ax.set_title('Price vs Sales Correlation', fontsize=13, fontweight='bold', pad=15)
        ax.legend(loc='upper right', fontsize=8, ncol=2)
        ax.grid(True, alpha=0.3)
        
        # 趋势线
        z = np.polyfit(data['价格'], data['销量'], 1)
        p = np.poly1d(z)
        ax.plot(data['价格'].sort_values(), p(data['价格'].sort_values()),
               "r--", alpha=0.5, linewidth=2)
        
        corr = data['价格'].corr(data['销量'])
        ax.text(0.05, 0.95, f'Correlation: {corr:.3f}', transform=ax.transAxes,
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    def _plot_trend(self, fig: plt.Figure, top_n: pd.DataFrame, position: int):
        """TOP3销量趋势折线图"""
        ax = fig.add_subplot(3, 2, position)
        
        days = pd.date_range(end=datetime.now(), periods=30, freq='D')
        top3 = top_n.head(3)
        
        for idx, (_, product) in enumerate(top3.iterrows()):
            base_sales = product['销量'] / 30
            trend = np.random.normal(1, 0.15, 30)
            for i, d in enumerate(days):
                if d.weekday() >= 5:
                    trend[i] *= 1.3
            daily_sales = np.maximum(base_sales * trend, base_sales * 0.3)
            
            ax.plot(days, daily_sales, marker='o', markersize=3, linewidth=1.5,
                   label=f"#{idx+1} ({product['销量']})", 
                   color=self.COLORS['top10'][idx])
        
        ax.set_xlabel('Date', fontsize=11)
        ax.set_ylabel('Daily Sales (Units)', fontsize=11)
        ax.set_title('TOP3 Products - 30 Days Trend', fontsize=13, fontweight='bold', pad=15)
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=30, labelsize=8)
    
    def _plot_heatmap(self, fig: plt.Figure, data: pd.DataFrame, position: int):
        """类目价格区间热力图"""
        ax = fig.add_subplot(3, 2, position)
        
        data['价格区间'] = pd.cut(data['价格'], bins=[0, 50, 100, 200, 500, 1000],
                               labels=['<50', '50-100', '100-200', '200-500', '>500'])
        
        pivot_sales = data.pivot_table(values='销量', index='类目', 
                                      columns='价格区间', aggfunc='mean')
        
        sns.heatmap(pivot_sales, annot=True, fmt='.0f', cmap='YlOrRd',
                   cbar_kws={'label': 'Avg Sales'}, ax=ax, linewidths=0.5,
                   annot_kws={'size': 8})
        ax.set_title('Category vs Price Range - Sales Heatmap', fontsize=13,
                    fontweight='bold', pad=15)
        ax.set_xlabel('Price Range (CNY)', fontsize=11)
        ax.set_ylabel('Category', fontsize=11)
        ax.tick_params(axis='both', labelsize=9)
    
    def _plot_comparison(self, fig: plt.Figure, top_n: pd.DataFrame,
                         bottom_n: pd.DataFrame, position: int):
        """爆款vs滞销品对比柱状图"""
        ax = fig.add_subplot(3, 2, position)
        
        metrics = ['Exposure\n(x1000)', 'CTR\n(%)', 'CVR\n(‰)', 'Fav+Cart\n(‰)']
        x = np.arange(len(metrics))
        width = 0.35
        
        top_values = [
            top_n['曝光量'].mean() / 1000,
            top_n['点击率'].mean() * 100,
            top_n['转化率'].mean() * 1000,
            top_n['收藏加购率'].mean() * 1000
        ]
        bottom_values = [
            bottom_n['曝光量'].mean() / 1000,
            bottom_n['点击率'].mean() * 100,
            bottom_n['转化率'].mean() * 1000,
            bottom_n['收藏加购率'].mean() * 1000
        ]
        
        bars1 = ax.bar(x - width/2, top_values, width, label='TOP10',
                      color=self.COLORS['primary'], edgecolor='white', linewidth=1)
        bars2 = ax.bar(x + width/2, bottom_values, width, label='Bottom 10',
                      color=self.COLORS['neutral'], edgecolor='white', linewidth=1)
        
        ax.set_ylabel('Value (Standardized)', fontsize=11)
        ax.set_title('TOP10 vs Bottom 10 - Metrics Comparison', fontsize=13,
                    fontweight='bold', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(metrics, fontsize=9)
        ax.legend(loc='upper right', fontsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # 数值标签
        for bar in bars1:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}', xy=(bar.get_x() + bar.get_width()/2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=8)
        
        for bar in bars2:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}', xy=(bar.get_x() + bar.get_width()/2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=8)


class ReportGenerator:
    """报告生成器类"""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
    
    def generate(self, data: pd.DataFrame, ranked_data: pd.DataFrame,
                 metrics: SalesMetrics, analysis_results: Dict):
        """生成完整分析报告"""
        logger.info("开始生成分析报告...")
        
        self._print_console_report(metrics, analysis_results)
        self._export_excel(data, ranked_data, metrics, analysis_results)
        
        logger.info("报告生成完成")
    
    def _print_console_report(self, metrics: SalesMetrics, analysis_results: Dict):
        """打印控制台报告"""
        print("\n" + "=" * 80)
        print("销售数据分析报告")
        print("=" * 80)
        
        print(f"\n【核心指标】")
        print(f"总销量: {metrics.total_sales:,} 件")
        print(f"TOP10销量占比: {metrics.top10_ratio:.2f}%")
        print(f"销量变异系数: {metrics.sales_cv:.2f}%")
        
        print(f"\n【类目分布】")
        for cat, count in analysis_results['category_distribution'].items():
            print(f"  {cat}: {count}款")
        
        print(f"\n【价格分析】")
        price = analysis_results['price_analysis']
        print(f"  TOP10均价: ¥{price['top_avg']:.2f}")
        print(f"  全店均价: ¥{price['all_avg']:.2f}")
        
        print(f"\n【运营指标对比】")
        print(analysis_results['operation_metrics'].to_string(index=False))
    
    def _export_excel(self, data: pd.DataFrame, ranked_data: pd.DataFrame,
                      metrics: SalesMetrics, analysis_results: Dict):
        """导出Excel报告"""
        output_path = self.config.output_dir / 'sales_analysis_report.xlsx'
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            ranked_data.to_excel(writer, sheet_name='完整排名', index=False)
            analysis_results['top_n'].to_excel(writer, sheet_name='TOP10', index=False)
            analysis_results['bottom_n'].to_excel(writer, sheet_name='BOTTOM10', index=False)
            
            # 类目汇总
            category_summary = data.groupby('类目').agg({
                '销量': ['sum', 'mean', 'count'],
                '销售额': 'sum',
                '转化率': 'mean'
            }).round(2)
            category_summary.to_excel(writer, sheet_name='类目汇总')
            
            # 核心指标
            summary_df = pd.DataFrame({
                '指标': ['总商品数', '总销量', 'TOP10占比', '销量标准差', '变异系数'],
                '数值': [len(data), metrics.total_sales, f"{metrics.top10_ratio:.2f}%",
                       f"{metrics.sales_std:.2f}", f"{metrics.sales_cv:.2f}%"]
            })
            summary_df.to_excel(writer, sheet_name='核心指标', index=False)
        
        print(f"\n✓ Excel报告已导出: {output_path}")


class SalesAnalysisPipeline:
    """分析流程编排类 - 主控制器"""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        self.config = config or AnalysisConfig()
        self.data_generator = DataGenerator(self.config)
        self.analyzer = SalesAnalyzer(self.config)
        self.visualizer = Visualizer(self.config)
        self.report_generator = ReportGenerator(self.config)
    
    def run(self) -> Dict[str, Any]:
        """执行完整分析流程"""
        logger.info("=" * 80)
        logger.info("开始执行销售数据分析流程")
        logger.info("=" * 80)
        
        try:
            # 1. 数据生成
            data = self.data_generator.generate()
            
            # 2. 数据分析
            ranked_data, metrics, analysis_results = self.analyzer.analyze(data)
            
            # 3. 可视化
            fig = self.visualizer.create_dashboard(
                data, analysis_results['top_n'], 
                analysis_results['bottom_n'], metrics
            )
            
            # 4. 报告生成
            self.report_generator.generate(data, ranked_data, metrics, analysis_results)
            
            logger.info("分析流程执行完成")
            
            return {
                'data': data,
                'ranked_data': ranked_data,
                'metrics': metrics,
                'analysis_results': analysis_results,
                'figure': fig
            }
            
        except Exception as e:
            logger.error(f"分析流程执行失败: {str(e)}", exc_info=True)
            raise


def main():
    """主函数"""
    # 创建配置
    config = AnalysisConfig(
        n_products=150,
        random_seed=42,
        output_dir=Path('.')
    )
    
    # 执行分析流程
    pipeline = SalesAnalysisPipeline(config)
    results = pipeline.run()
    
    return results


if __name__ == "__main__":
    results = main()
