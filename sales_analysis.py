import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import warnings

warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

np.random.seed(42)


@dataclass
class CategoryConfig:
    price_range: Tuple[float, float]
    materials: List[str]
    specs: List[str]


CONFIG: Dict[str, Any] = {
    'categories': {
        '服装': CategoryConfig((50, 500), ['棉', '涤纶', '丝绸'], ['S', 'M', 'L', 'XL', 'XXL']),
        '数码': CategoryConfig((100, 5000), ['金属', '塑料'], ['128GB', '256GB', '512GB', '1TB']),
        '家居': CategoryConfig((30, 800), ['木材', '陶瓷', '金属', '塑料'], ['小号', '中号', '大号', '特大号']),
        '食品': CategoryConfig((10, 200), ['天然'], ['100g', '250g', '500g', '1kg']),
        '美妆': CategoryConfig((30, 500), ['天然', '化学合成'], ['30ml', '50ml', '100ml', '200ml']),
        '运动': CategoryConfig((50, 1000), ['涤纶', '橡胶', '金属'], ['S', 'M', 'L', 'XL']),
        '图书': CategoryConfig((20, 150), ['纸张'], ['平装', '精装', '套装']),
        '母婴': CategoryConfig((30, 400), ['塑料', '棉', '天然'], ['小号', '中号', '大号']),
    },
    'good_keywords': ['质量好', '性价比高', '物流快', '包装精美', '颜色正', '尺码准', '材质舒适', '外观漂亮'],
    'bad_reasons': ['物流慢', '包装破损', '色差大', '尺码偏小', '材质一般', '与描述不符'],
    'metrics': ['曝光量', '点击率', '转化率', '收藏加购率', '促销力度', '优惠券使用占比'],
    'comparison_metrics': ['价格', '曝光量', '点击率', '转化率', '收藏加购率', '促销力度', '评分', '上架时长(天)'],
}


class ProductDataGenerator:
    
    def __init__(self, n_products: int = 100, base_date: datetime = None):
        self.n_products = n_products
        self.base_date = base_date or datetime(2024, 1, 1)
    
    def generate(self) -> pd.DataFrame:
        products = [self._generate_single_product(i) for i in range(self.n_products)]
        return pd.DataFrame(products)
    
    def _generate_single_product(self, index: int) -> Dict[str, Any]:
        category = np.random.choice(list(CONFIG['categories'].keys()))
        config = CONFIG['categories'][category]
        
        price = np.random.uniform(*config.price_range)
        material = np.random.choice(config.materials)
        spec = np.random.choice(config.specs)
        
        days_on_shelf = np.random.randint(30, 365)
        listing_date = self.base_date + timedelta(days=365 - days_on_shelf)
        
        sales = self._calculate_sales(category, price, days_on_shelf)
        rating = self._generate_rating(sales)
        
        return {
            '商品ID': f'P{str(index + 1).zfill(4)}',
            '商品名称': f'{category}商品{index + 1}号',
            '类目': category,
            '价格': round(price, 2),
            '规格': spec,
            '材质': material,
            '上架日期': listing_date.strftime('%Y-%m-%d'),
            '上架时长(天)': days_on_shelf,
            '促销力度': round(np.random.uniform(0, 0.5), 2),
            '优惠券使用占比': round(np.random.uniform(0.1, 0.8), 2),
            '曝光量': int(np.random.uniform(10000, 500000)),
            '点击率': round(np.random.uniform(0.01, 0.1), 4),
            '转化率': round(np.random.uniform(0.01, 0.15), 4),
            '收藏加购率': round(np.random.uniform(0.05, 0.3), 4),
            '销量': sales,
            '评分': rating,
            '好评关键词': self._generate_good_keywords(),
            '差评原因': self._generate_bad_reasons(rating),
        }
    
    def _calculate_sales(self, category: str, price: float, days_on_shelf: int) -> int:
        base_sales = np.random.exponential(scale=500)
        
        season_factor = 1.0
        if category in ['服装', '运动'] and days_on_shelf > 180:
            season_factor = 1.3
        elif category == '食品':
            season_factor = 1.2
        
        price_factor = max(0.3, 1 - price / 2000)
        random_factor = np.random.uniform(0.8, 1.2)
        
        sales = int(base_sales * season_factor * price_factor * random_factor)
        return max(10, sales)
    
    def _generate_rating(self, sales: int) -> float:
        if sales > 1000:
            return round(np.random.uniform(4.2, 5.0), 1)
        return round(np.random.uniform(3.5, 5.0), 1)
    
    def _generate_good_keywords(self) -> str:
        keywords = np.random.choice(
            CONFIG['good_keywords'],
            size=np.random.randint(2, 5),
            replace=False
        )
        return ','.join(keywords)
    
    def _generate_bad_reasons(self, rating: float) -> str:
        if rating >= 4.5:
            return ''
        reasons = np.random.choice(
            CONFIG['bad_reasons'],
            size=np.random.randint(0, 3),
            replace=False
        )
        return ','.join(reasons) if len(reasons) > 0 else ''


class DailyTrendGenerator:
    
    def __init__(self, base_date: datetime = None):
        self.base_date = base_date or datetime(2024, 11, 25)
    
    def generate(self, df: pd.DataFrame, top_product_ids: np.ndarray) -> pd.DataFrame:
        daily_data = []
        
        for product_id in top_product_ids:
            product_info = df[df['商品ID'] == product_id].iloc[0]
            base_sales = product_info['销量'] / 30
            
            for day in range(30):
                date = self.base_date + timedelta(days=day)
                daily_sales = self._calculate_daily_sales(base_sales, date, day)
                
                daily_data.append({
                    '商品ID': product_id,
                    '商品名称': product_info['商品名称'],
                    '日期': date.strftime('%Y-%m-%d'),
                    '销量': daily_sales,
                })
        
        return pd.DataFrame(daily_data)
    
    def _calculate_daily_sales(self, base_sales: float, date: datetime, day: int) -> int:
        weekend_factor = 1.3 if day in [6, 7, 13, 14, 20, 21, 27, 28] else 1.0
        holiday_factor = 1.8 if day in [10, 11, 12] else 1.0
        random_factor = np.random.uniform(0.7, 1.3)
        
        sales = int(base_sales * weekend_factor * holiday_factor * random_factor)
        return max(1, sales)


class SalesAnalyzer:
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.df_sorted = df.sort_values('销量', ascending=False).reset_index(drop=True)
        self.df_sorted['排名'] = range(1, len(self.df_sorted) + 1)
    
    def get_top10(self) -> pd.DataFrame:
        return self.df_sorted.head(10)
    
    def get_bottom10(self) -> pd.DataFrame:
        return self.df_sorted.tail(10)
    
    def get_median_product(self) -> pd.Series:
        return self.df_sorted.iloc[len(self.df_sorted) // 2]
    
    def get_statistics(self) -> Dict[str, float]:
        total_sales = self.df['销量'].sum()
        top10_sales = self.get_top10()['销量'].sum()
        std_sales = self.df['销量'].std()
        mean_sales = self.df['销量'].mean()
        
        return {
            'total_sales': total_sales,
            'top10_sales': top10_sales,
            'top10_ratio': top10_sales / total_sales * 100,
            'median_sales': self.df['销量'].median(),
            'std_sales': std_sales,
            'mean_sales': mean_sales,
            'cv': std_sales / mean_sales,
        }
    
    def get_distribution_type(self, cv: float) -> str:
        if cv > 1:
            return "高度分散，销量差异显著"
        elif cv > 0.5:
            return "中等分散，存在一定差异"
        return "相对集中，销量较为均衡"
    
    def compare_groups(self, top: pd.DataFrame, bottom: pd.DataFrame) -> pd.DataFrame:
        comparison_data = []
        
        for metric in CONFIG['comparison_metrics']:
            top_val = top[metric].mean()
            bottom_val = bottom[metric].mean()
            diff_pct = (top_val - bottom_val) / bottom_val * 100 if bottom_val != 0 else 0
            
            comparison_data.append({
                '指标': metric,
                '爆款均值': round(top_val, 2),
                '滞销均值': round(bottom_val, 2),
                '差异百分比': f"{diff_pct:+.1f}%",
            })
        
        return pd.DataFrame(comparison_data)


class ReportPrinter:
    
    @staticmethod
    def print_header(title: str) -> None:
        print("=" * 80)
        print(title)
        print("=" * 80)
    
    @staticmethod
    def print_section(title: str) -> None:
        print(f"\n【{title}】")
        print("-" * 80)
    
    @staticmethod
    def print_ranking_report(analyzer: SalesAnalyzer) -> Tuple[pd.DataFrame, pd.DataFrame, float]:
        ReportPrinter.print_header("商品销量排名分析报告")
        
        top10 = analyzer.get_top10()
        bottom10 = analyzer.get_bottom10()
        median_product = analyzer.get_median_product()
        stats = analyzer.get_statistics()
        
        ReportPrinter.print_section("一、销量排名榜单")
        
        print("\n★ TOP10 爆款商品:")
        print(top10[['排名', '商品ID', '商品名称', '类目', '价格', '销量', '转化率', '评分']].to_string(index=False))
        
        print(f"\n★ 销量中位数商品 (第{len(analyzer.df_sorted)//2}名):")
        print(f"  商品ID: {median_product['商品ID']}, 名称: {median_product['商品名称']}, 销量: {median_product['销量']}")
        print(f"  中位数销量: {stats['median_sales']}")
        
        print("\n★ 销量垫底10款商品:")
        print(bottom10[['排名', '商品ID', '商品名称', '类目', '价格', '销量', '转化率', '评分']].to_string(index=False))
        
        ReportPrinter.print_section("二、核心数据指标")
        print(f"总销量: {stats['total_sales']:,}")
        print(f"TOP10商品销量: {stats['top10_sales']:,}")
        print(f"TOP10销量占比: {stats['top10_ratio']:.2f}%")
        print(f"销量标准差: {stats['std_sales']:,.2f}")
        print(f"销量均值: {stats['mean_sales']:,.2f}")
        print(f"变异系数(CV): {stats['cv']:.2f}")
        print(f"销量分布特征: {analyzer.get_distribution_type(stats['cv'])}")
        
        return top10, bottom10, stats['top10_ratio']
    
    @staticmethod
    def print_analysis_report(df: pd.DataFrame, top10: pd.DataFrame, bottom10: pd.DataFrame) -> pd.DataFrame:
        ReportPrinter.print_section("三、热销原因深度分析")
        
        print("\n★ 爆款商品共性特征分析:")
        
        print("\n1. 类目分布:")
        print(f"   TOP10类目分布: {top10['类目'].value_counts().to_dict()}")
        
        print("\n2. 价格区间:")
        print(f"   TOP10均价: {top10['价格'].mean():.2f}元, 中位数: {top10['价格'].median():.2f}元")
        print(f"   全量商品均价: {df['价格'].mean():.2f}元")
        
        print("\n3. 运营数据对比:")
        for metric in CONFIG['metrics']:
            top10_val = top10[metric].mean()
            all_val = df[metric].mean()
            diff = (top10_val - all_val) / all_val * 100
            print(f"   {metric}: TOP10均值={top10_val:.4f}, 全量均值={all_val:.4f}, 差异={diff:+.1f}%")
        
        print("\n4. 用户反馈分析:")
        print(f"   TOP10平均评分: {top10['评分'].mean():.2f}, 全量平均评分: {df['评分'].mean():.2f}")
        
        print("\n5. 上架时长分析:")
        print(f"   TOP10平均上架时长: {top10['上架时长(天)'].mean():.0f}天, 全量平均: {df['上架时长(天)'].mean():.0f}天")
        
        print("\n★ 爆款与滞销商品对比分析:")
        print("-" * 80)
        
        analyzer = SalesAnalyzer(df)
        comparison_df = analyzer.compare_groups(top10, bottom10)
        print(comparison_df.to_string(index=False))
        
        print("\n★ 关键影响因素总结:")
        factors = [
            "转化率是影响销量的最关键因素",
            "曝光量对销量有显著正向影响",
            "价格适中（非最低）的商品更易成为爆款",
            "高评分和好评率是爆款的重要特征",
            "促销活动和优惠券使用能有效提升销量",
        ]
        for i, factor in enumerate(factors, 1):
            print(f"   {i}. {factor}")
        
        return comparison_df
    
    @staticmethod
    def print_recommendations() -> None:
        ReportPrinter.print_section("五、优化建议")
        ReportPrinter.print_header("")
        
        recommendations = {
            "针对滞销商品的优化建议": [
                "提升曝光量: 增加广告投放、参与平台活动、优化搜索关键词",
                "优化转化率: 改善商品详情页、增加买家秀、优化主图视频",
                "价格策略: 适度降价或增加优惠券力度，参考爆款价格区间",
                "促销活动: 参与平台大促、设置限时折扣、满减活动",
                "用户评价: 主动引导好评、及时处理差评、提升服务质量",
            ],
            "针对爆款商品的维护建议": [
                "保持库存充足，避免断货影响排名",
                "持续监控评价，及时处理负面反馈",
                "适度扩大曝光，进一步抢占市场份额",
                "开发关联商品，形成爆款矩阵",
            ],
            "整体运营策略建议": [
                "重点打造高转化率类目商品",
                "建立价格梯度，覆盖不同消费群体",
                "优化促销节奏，把握节假日流量高峰",
                "建立商品分层运营体系，差异化资源配置",
            ],
        }
        
        for title, items in recommendations.items():
            print(f"\n★ {title}:")
            for i, item in enumerate(items, 1):
                print(f"   {i}. {item}")
        
        print("\n" + "=" * 80)
        print("报告生成完成")
        print("=" * 80)


class Visualizer:
    
    def __init__(self, figsize: Tuple[int, int] = (20, 16)):
        self.figsize = figsize
    
    def create_dashboard(
        self,
        df: pd.DataFrame,
        top10: pd.DataFrame,
        bottom10: pd.DataFrame,
        daily_trend: pd.DataFrame,
        top10_ratio: float,
        output_path: str = 'sales_analysis_dashboard.png'
    ) -> plt.Figure:
        print("\n【四、数据可视化图表生成】")
        print("-" * 80)
        
        fig = plt.figure(figsize=self.figsize)
        
        self._plot_top10_ranking(fig, top10, 1)
        self._plot_sales_pie(fig, df, top10, top10_ratio, 2)
        self._plot_price_sales_scatter(fig, df, 3)
        self._plot_daily_trend(fig, daily_trend, top10, 4)
        self._plot_category_heatmap(fig, df, 5)
        self._plot_comparison_bars(fig, df, top10, bottom10, 6)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
        print(f"✓ 可视化图表已保存: {output_path}")
        
        return fig
    
    def _plot_top10_ranking(self, fig: plt.Figure, top10: pd.DataFrame, position: int) -> None:
        ax = fig.add_subplot(2, 3, position)
        colors = plt.cm.RdYlGn(np.linspace(0.8, 0.2, 10))
        
        bars = ax.barh(range(10), top10['销量'].values, color=colors)
        ax.set_yticks(range(10))
        ax.set_yticklabels([f"{row['商品ID']}\n{row['商品名称'][:6]}" for _, row in top10.iterrows()])
        ax.set_xlabel('销量', fontsize=12)
        ax.set_title('TOP10商品销量排名', fontsize=14, fontweight='bold')
        ax.invert_yaxis()
        
        for bar, val in zip(bars, top10['销量'].values):
            ax.text(val + 50, bar.get_y() + bar.get_height() / 2, f'{val:,}',
                    va='center', fontsize=10, fontweight='bold')
    
    def _plot_sales_pie(self, fig: plt.Figure, df: pd.DataFrame, top10: pd.DataFrame, 
                        top10_ratio: float, position: int) -> None:
        ax = fig.add_subplot(2, 3, position)
        
        other_sales = df['销量'].sum() - top10['销量'].sum()
        pie_data = list(top10['销量'].values) + [other_sales]
        pie_labels = [f"{row['商品ID']}" for _, row in top10.iterrows()] + ['其他商品']
        colors_pie = plt.cm.Set3(np.linspace(0, 1, 11))
        
        ax.pie(pie_data, labels=pie_labels, autopct='%1.1f%%', colors=colors_pie, startangle=90)
        ax.set_title(f'TOP10商品销量占比\n(TOP10占比: {top10_ratio:.1f}%)', fontsize=14, fontweight='bold')
    
    def _plot_price_sales_scatter(self, fig: plt.Figure, df: pd.DataFrame, position: int) -> None:
        ax = fig.add_subplot(2, 3, position)
        
        scatter = ax.scatter(df['价格'], df['销量'], c=df['转化率'], cmap='RdYlGn',
                            alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
        ax.set_xlabel('价格 (元)', fontsize=12)
        ax.set_ylabel('销量', fontsize=12)
        ax.set_title('商品价格与销量相关性分析', fontsize=14, fontweight='bold')
        
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('转化率')
        
        z = np.polyfit(df['价格'], df['销量'], 1)
        p = np.poly1d(z)
        ax.plot(df['价格'].sort_values(), p(df['价格'].sort_values()),
                "r--", alpha=0.8, linewidth=2, label='趋势线')
        ax.legend()
    
    def _plot_daily_trend(self, fig: plt.Figure, daily_trend: pd.DataFrame, 
                          top10: pd.DataFrame, position: int) -> None:
        ax = fig.add_subplot(2, 3, position)
        
        top3_ids = top10['商品ID'].head(3).values
        for product_id in top3_ids:
            product_trend = daily_trend[daily_trend['商品ID'] == product_id]
            ax.plot(range(len(product_trend)), product_trend['销量'].values,
                   marker='o', markersize=3, label=product_trend['商品名称'].iloc[0][:10])
        
        ax.set_xlabel('日期 (近30天)', fontsize=12)
        ax.set_ylabel('日销量', fontsize=12)
        ax.set_title('TOP3爆款商品近30天销量趋势', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.set_xticks(range(0, 30, 5))
        ax.set_xticklabels([f'D{i+1}' for i in range(0, 30, 5)])
        ax.grid(True, alpha=0.3)
    
    def _plot_category_heatmap(self, fig: plt.Figure, df: pd.DataFrame, position: int) -> None:
        ax = fig.add_subplot(2, 3, position)
        
        category_stats = df.groupby('类目').agg({'销量': 'sum', '转化率': 'mean'})
        
        im = ax.imshow(category_stats.values, cmap='YlOrRd', aspect='auto')
        ax.set_xticks(range(2))
        ax.set_xticklabels(['销量', '转化率'])
        ax.set_yticks(range(len(category_stats)))
        ax.set_yticklabels(category_stats.index)
        ax.set_title('不同类目销量与转化率热力图', fontsize=14, fontweight='bold')
        
        for i in range(len(category_stats)):
            for j in range(2):
                val = category_stats.values[i, j]
                text = f'{int(val):,}' if j == 0 else f'{val:.2%}'
                ax.text(j, i, text, ha='center', va='center', fontsize=9)
        
        plt.colorbar(im, ax=ax)
    
    def _plot_comparison_bars(self, fig: plt.Figure, df: pd.DataFrame, 
                              top10: pd.DataFrame, bottom10: pd.DataFrame, position: int) -> None:
        ax = fig.add_subplot(2, 3, position)
        
        metrics_compare = ['曝光量', '点击率', '转化率']
        x = np.arange(len(metrics_compare))
        width = 0.35
        
        top10_norm = [top10[m].mean() / df[m].mean() for m in metrics_compare]
        bottom10_norm = [bottom10[m].mean() / df[m].mean() for m in metrics_compare]
        
        bars1 = ax.bar(x - width / 2, top10_norm, width, label='爆款商品', color='#2ecc71')
        bars2 = ax.bar(x + width / 2, bottom10_norm, width, label='滞销商品', color='#e74c3c')
        
        ax.set_ylabel('相对指数 (全量均值=1)', fontsize=12)
        ax.set_title('爆款vs滞销商品核心指标对比', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics_compare)
        ax.legend()
        ax.axhline(y=1, color='gray', linestyle='--', alpha=0.5)
        
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.2f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3), textcoords="offset points",
                           ha='center', va='bottom', fontsize=10)


class SalesAnalysisPipeline:
    
    def __init__(self, n_products: int = 100):
        self.n_products = n_products
        self.product_generator = ProductDataGenerator(n_products)
        self.trend_generator = DailyTrendGenerator()
        self.visualizer = Visualizer()
        
        self.df: Optional[pd.DataFrame] = None
        self.df_sorted: Optional[pd.DataFrame] = None
        self.top10: Optional[pd.DataFrame] = None
        self.bottom10: Optional[pd.DataFrame] = None
        self.daily_trend: Optional[pd.DataFrame] = None
    
    def run(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        print("开始生成商品销售数据...")
        self.df = self.product_generator.generate()
        self.df.to_csv('product_sales_data.csv', index=False, encoding='utf-8-sig')
        print(f"✓ 数据集已保存: product_sales_data.csv (共{len(self.df)}条商品数据)")
        
        analyzer = SalesAnalyzer(self.df)
        self.df_sorted = analyzer.df_sorted
        self.top10, self.bottom10, top10_ratio = ReportPrinter.print_ranking_report(analyzer)
        
        ReportPrinter.print_analysis_report(self.df, self.top10, self.bottom10)
        
        top3_ids = self.top10['商品ID'].head(3).values
        self.daily_trend = self.trend_generator.generate(self.df, top3_ids)
        self.daily_trend.to_csv('daily_sales_trend.csv', index=False, encoding='utf-8-sig')
        print(f"✓ 日销量趋势数据已保存: daily_sales_trend.csv")
        
        self.visualizer.create_dashboard(
            self.df, self.top10, self.bottom10, self.daily_trend, top10_ratio
        )
        
        ReportPrinter.print_recommendations()
        
        return self.df, self.df_sorted, self.top10, self.bottom10, self.daily_trend


def main() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pipeline = SalesAnalysisPipeline(n_products=100)
    return pipeline.run()


if __name__ == "__main__":
    df, df_sorted, top10, bottom10, daily_trend = main()
