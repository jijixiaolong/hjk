import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# 页面配置
st.set_page_config(
    page_title="航空工程学院学生数据分析系统",
    page_icon="👨‍🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS样式
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
    color: white;
    padding: 1rem;
    margin-bottom: 1rem;
    text-align: center;
}

/* 移除卡片样式 */
.card {
    padding: 1rem;
    margin-bottom: 1rem;
    background: transparent;
    border: none;
    box-shadow: none;
}

/* 去掉卡片彩色边条 */
.card::before {
    display: none;
}

.info-row {
    display: flex;
    padding: 0.5rem 0;
    border-bottom: 1px solid #f3f4f6;
}

.info-label {
    color: #6b7280;
    font-weight: 500;
    width: 50%;
    text-align: left;
}

.info-value {
    font-weight: 600;
    color: #1f2937;
    width: 50%;
    text-align: center;
}

.status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
}

.status-help {
    background-color: #fee2e2;
    color: #dc2626;
}

.status-no-help {
    background-color: #dcfce7;
    color: #16a34a;
}

.status-scholarship {
    background-color: #fef3c7;
    color: #d97706;
}

.status-none {
    background-color: #f3f4f6;
    color: #6b7280;
}

/* 心理评测等级专用样式 */
.psych-level-3 {
    background-color: #dcfce7;
    color: #16a34a;
}

.psych-level-2 {
    background-color: #fef3c7;
    color: #d97706;
}

.psych-level-1 {
    background-color: #fee2e2;
    color: #dc2626;
}

.metric-card {
    text-align: center;
    padding: 1rem;  /* 增加了内边距 */
    margin: 0.5rem; /* 增加了外边距 */
    background: #ffffff; /* 白色背景 */
    border: 1px solid #e2e8f0; /* 浅灰色边框 */
    border-radius: 8px; /* 圆角 */
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); /* 轻微阴影 */
}

.gpa-summary {
    color: #1f2937;
    padding: 0.8rem;
    text-align: center;
    margin: 0.5rem 0;
    background: transparent;
    border: none;
    box-shadow: none;
}

/* 调整间距 */
div.block-container {
    padding-top: 1rem !important;
}

/* 移除Streamlit元素之间的多余间距 */
.element-container {
    margin-bottom: 0.5rem !important;
}

/* 简化图表样式 */
.js-plotly-plot {
    border: none;
    box-shadow: none;
    background-color: transparent;
    padding: 0;
}

/* 移除所有可能的边框和阴影 */
div, section {
    /* border: none !important; */ /* 暂时注释掉，允许metric-card有边框 */
    /* box-shadow: none !important; */ /* 暂时注释掉，允许metric-card有阴影 */
}
</style>
""", unsafe_allow_html=True)

# 工具函数：处理空值显示
def format_value(value):
    """将空值、NaN、None等转换为'无'"""
    if pd.isna(value) or value is None or str(value).lower() in ['nan', 'none', '']:
        return '无'
    return str(value)

# 初始化session state
if 'students_data' not in st.session_state:
    st.session_state.students_data = None
if 'selected_student_index' not in st.session_state:
    st.session_state.selected_student_index = 0

# 主标题
st.markdown("""
<div class="main-header">
    <h1>👨‍🎓 航空工程学院学生数据分析系统</h1>
</div>
""", unsafe_allow_html=True)

# 文件上传区域
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 📊 数据上传")

# 在这里添加表头要求信息
required_columns_list_for_info = [
    "序号", "学号", "姓名", "原班级", "新班级", "原专业", "分流专业", "辅导员", "政治面貌",
    "入团申请书编号", "是否递交入党申请书", "是否积极分子", "民族", "性别", "是否过四级", "是否过六级",
    "第一学期绩点", "第二学期绩点", "第三学期绩点", "第一学年德育", "第一学年智育", "第一学年附加分",
    "第一学年体测成绩", "第一学年体测评级", "第一学年综测总分", "心理评测等级", "第一学年困难等级",
    "第二学年困难等级", "有无需要学院协助解决的困难", "有何困难", "去年困难生", "今年困难生",
    "挂科", "所获学分", "奖项", "人民奖学金", "助学奖学金", "助学金"
]
info_message = "💡 **请确保上传的 Excel 文件包含以下列（表头名称需完全一致）：**\n\n"
# 每行显示几个字段，避免列表过长
columns_per_row = 6 
for i in range(0, len(required_columns_list_for_info), columns_per_row):
    info_message += "- " + ", ".join(f"`{col}`" for col in required_columns_list_for_info[i:i+columns_per_row]) + "\n"

st.info(info_message)

uploaded_file = st.file_uploader(
    "选择Excel文件上传学生数据",
    type=['xlsx', 'xls'],
    help="支持Excel格式文件。上传前请参考上方列表确保表头正确。" # 更新help文本
)

if uploaded_file is not None:
    try:
        # 读取Excel文件
        df = pd.read_excel(uploaded_file)

        # 在这里插入表头检查逻辑
        # 定义必需的表头列表
        required_columns = [
            "序号", "学号", "姓名", "原班级", "新班级", "原专业", "分流专业", "辅导员", "政治面貌",
            "入团申请书编号", "是否递交入党申请书", "是否积极分子", "民族", "性别", "是否过四级", "是否过六级",
            "第一学期绩点", "第二学期绩点", "第三学期绩点", "第一学年德育", "第一学年智育", "第一学年附加分",
            "第一学年体测成绩", "第一学年体测评级", "第一学年综测总分", "心理评测等级", "第一学年困难等级",
            "第二学年困难等级", "有无需要学院协助解决的困难", "有何困难", "去年困难生", "今年困难生",
            "挂科", "所获学分", "奖项", "人民奖学金", "助学奖学金", "助学金"
        ]

        # 检查缺失字段
        missing_columns = [col for col in required_columns if col not in df.columns]

        # 如果有缺失，报错并阻止后续流程
        if missing_columns:
            st.error(f"❌ Excel文件校验失败：缺少以下必需的列名，请检查文件后重新上传：\n\n{', '.join(missing_columns)}")
            st.session_state.students_data = None # 清空数据，阻止后续执行
            # 使用 st.stop() 会完全停止脚本，如果希望只是阻止后续UI渲染，可以不加
            # st.stop() 
        else:
            # 如果表头检查通过，才将数据存入 session_state
            st.session_state.students_data = df
            st.success(f"✅ 成功加载 {len(df)} 名学生的数据，表头校验通过。")

    except Exception as e:
        st.error(f"❌ 文件读取或处理失败: {str(e)}")
        st.session_state.students_data = None

st.markdown('</div>', unsafe_allow_html=True)

# 如果没有数据，显示欢迎界面
if st.session_state.students_data is None:
    st.markdown("""
    <div class="card" style="text-align: center; padding: 3rem;">
        <h3>🎯 欢迎使用学生数据分析系统</h3>
        <p style="color: #6b7280; margin: 1rem 0;">请上传Excel文件开始分析学生数据</p>
        <p style="color: #9ca3af; font-size: 0.9rem;">支持学生基本信息、成绩、奖学金等多维度数据分析</p>
    </div>
    """, unsafe_allow_html=True)
else:
    df = st.session_state.students_data
    
    # 学生选择器
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🔍 学生选择器")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        # 搜索功能
        search_term = st.text_input("🔍 搜索学生", placeholder="输入姓名、学号或班级进行搜索...")
        
        # 过滤学生数据
        if search_term:
            mask = (
                df['姓名'].astype(str).str.contains(search_term, case=False, na=False) |
                df['学号'].astype(str).str.contains(search_term, case=False, na=False) |
                df.apply(lambda row: any(
                    str(val).lower().find(search_term.lower()) != -1
                    for col in ['班级', '班级_基本信息', '班 级', '班 级_基本信息'] 
                    if col in df.columns 
                    for val in [row.get(col, '')] 
                    if pd.notna(val)
                ), axis=1)
            )
            filtered_df = df[mask]
        else:
            filtered_df = df
    
    with col2:
        st.metric("总学生数", len(df))
    
    with col3:
        st.metric("筛选结果", len(filtered_df))
    
    if len(filtered_df) > 0:
        # 学生选择下拉框
        student_options = []
        for idx, row in filtered_df.iterrows():
            # 获取班级值，尝试多种可能的列名
            班级值 = ''
            for col in ['班级', '班级_基本信息', '班 级', '班 级_基本信息']:
                if col in filtered_df.columns and pd.notna(row.get(col)):
                    班级值 = row.get(col)
                    break
                    
            student_options.append(f"{format_value(row['姓名'])} - {format_value(row['学号'])} ")
        
        selected_student = st.selectbox(
            "选择学生",
            options=range(len(student_options)),
            format_func=lambda x: student_options[x],
            key="student_selector"
        )
        
        # 导航按钮
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("⬅️ 上一个", disabled=selected_student == 0):
                selected_student = max(0, selected_student - 1)
        with col3:
            if st.button("下一个 ➡️", disabled=selected_student >= len(student_options) - 1):
                selected_student = min(len(student_options) - 1, selected_student + 1)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 获取选中的学生数据
        student_data = filtered_df.iloc[selected_student]
        
        # 个人信息卡片
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 👤 个人信息")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="info-row">
                <span class="info-label">姓名：</span>
                <span class="info-value">{format_value(student_data.get('姓名'))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">分流专业：</span>
                <span class="info-value">{format_value(student_data.get('分流专业'))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">新班级：</span>
                <span class="info-value">{format_value(student_data.get('新班级') or student_data.get('班级_基本信息') or student_data.get('班 级_基本信息') or student_data.get('班级') or student_data.get('班 级'))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">辅导员：</span>
                <span class="info-value">{format_value(student_data.get('辅导员'))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">民族：</span>
                <span class="info-value">{format_value(student_data.get('民族'))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">是否积极分子：</span>
                <span class="info-value">{format_value(student_data.get('是否积极分子'))}</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="info-row">
                <span class="info-label">学号：</span>
                <span class="info-value">{format_value(student_data.get('学号'))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">原专业：</span>
                <span class="info-value">{format_value(student_data.get('原专业'))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">原班级：</span>
                <span class="info-value">{format_value(student_data.get('原班级', student_data.get('班级')))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">政治面貌：</span>
                <span class="info-value">{format_value(student_data.get('政治面貌'))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">性别：</span>
                <span class="info-value">{format_value(student_data.get('性别'))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">是否递交入党申请书：</span>
                <span class="info-value">{format_value(student_data.get('是否递交入党申请书'))}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 帮助需求卡片
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🆘 帮助需求")
        
        help_needed_value = student_data.get('有无需要学院协助解决的困难')
        help_needed = (
            help_needed_value and 
            not pd.isna(help_needed_value) and
            str(help_needed_value).lower() not in ['无', 'nan', 'none', '']
        )
        
        if help_needed:
            st.markdown(f"""
            <div style="background: #fee2e2; padding: 1rem; border-radius: 8px; border: 1px solid #fecaca;">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <div style="width: 12px; height: 12px; background: #dc2626; border-radius: 50%; margin-right: 0.5rem;"></div>
                    <span style="font-weight: 600; color: #dc2626;">需要帮助</span>
                </div>
                <p style="color: #dc2626; margin: 0; font-size: 0.9rem;">
                    困难详情: {format_value(student_data.get('有何困难', '未详述'))}
                </p>
                <p style="color: #6b7280; margin-top: 0.5rem; font-size: 0.8rem;">
                    心理状态: {format_value(student_data.get('最新心理等级', '未评估'))}
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #dcfce7; padding: 1rem; border-radius: 8px; border: 1px solid #bbf7d0;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 12px; height: 12px; background: #16a34a; border-radius: 50%; margin-right: 0.5rem;"></div>
                    <span style="font-weight: 600; color: #16a34a;">无需帮助</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        # 心理评测等级模块
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 💖 心理评测等级")
        
        # 获取心理评测等级
        psychological_level = student_data.get('心理评测等级', student_data.get('最新心理等级', student_data.get('心理等级')))
        psych_value = format_value(psychological_level)
        
        # 根据心理等级设置不同的样式和描述
        if psych_value in ['3级', '3', 'III级', 'III', '三级']:
            status_class = "psych-level-3"
            description = "心理健康状况良好，正常"
        elif psych_value in ['2级', '2', 'II级', 'II', '二级']:
            status_class = "psych-level-2"
            description = "存在轻微心理问题，建议关注"
        elif psych_value in ['1级', '1', 'I级', 'I', '一级']:
            status_class = "psych-level-1"
            description = "存在严重心理问题，需要专业帮助"
        else:
            status_class = "status-none"
            description = "暂无心理评测数据"
        
        # 显示心理评测等级
        st.markdown(f"""
        <div style="background: #f0f4f8; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid #e2e8f0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span style="color: #4b5563; font-weight: 600;">心理评测等级：</span>
                <span class="status-badge {status_class}">{psych_value}</span>
            </div>
            <div style="color: #4b5563; font-size: 0.95rem; margin-top: 0.5rem;">
                {description}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        # 咨询问题卡片
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 💜贫困等级")
        
        consultation_items = [
            "第一学年困难等级",
            "第二学年困难等级"
        ]
        
        # 直接生成所有内容的HTML，避免streamlit自动添加额外元素
        html_content = ""
        for item in consultation_items:
            raw_value = student_data.get(item)
            value = format_value(raw_value)
            status_class = "status-help" if value != '无' else "status-none"
            html_content += f"""
            <div style="background: #f8fafc; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #6b7280;">{item}：</span>
                    <span class="status-badge {status_class}">{value}</span>
                </div>
            </div>
            """
        
        st.markdown(html_content, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 奖学金信息卡片
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🏆 奖学金信息")
        
        scholarship_items = [
            ("人民奖学金", student_data.get('人民奖学金')),
            ("助学奖学金", student_data.get('助学奖学金')),
            ("助学金", student_data.get('助学金', student_data.get('助学金.1'))),
            ("获得奖项", student_data.get('奖项'))
        ]
        
        for label, raw_value in scholarship_items:
            value = format_value(raw_value)
            status_class = "status-scholarship" if value != '无' else "status-none"
            st.markdown(f"""
            <div style="background: #fffbeb; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #6b7280;">{label}：</span>
                    <span class="status-badge {status_class}">{value}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 综合素质雷达图
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📊 综合素质雷达图")
        
        # 准备雷达图数据
        def normalize_value(value, min_val, max_val):
            if pd.isna(value) or value is None:
                return 0
            try:
                float_value = float(value)
                return max(0, min(100, ((float_value - min_val) / (max_val - min_val)) * 100))
            except (ValueError, TypeError):
                return 0
        
        def get_display_value(value):
            if pd.isna(value) or value is None:
                return 0
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0
        
        radar_data = [
            ("第一学年德育", normalize_value(student_data.get('第一学年德育', student_data.get('德育')), 12, 15), get_display_value(student_data.get('第一学年德育', student_data.get('德育')))),
            ("第一学年智育", normalize_value(student_data.get('第一学年智育', student_data.get('智育')), 15,80), get_display_value(student_data.get('第一学年智育', student_data.get('智育')))),
            ("第一学年体测", normalize_value(student_data.get('第一学年体测成绩', student_data.get('体测成绩')), 15, 110), get_display_value(student_data.get('第一学年体测成绩', student_data.get('体测成绩')))),
            ("第一学年附加分", normalize_value(student_data.get('第一学年附加分', student_data.get('附加分', student_data.get('23-24附加分'))), -1, 6), get_display_value(student_data.get('第一学年附加分', student_data.get('附加分', student_data.get('23-24附加分'))))),
            ("第一学年总分", normalize_value(student_data.get('第一学年综测总分', student_data.get('第一学年总分', student_data.get('测评总分'))), 20, 100), get_display_value(student_data.get('第一学年综测总分', student_data.get('第一学年总分', student_data.get('测评总分')))))
        ]
        
        categories = [item[0] for item in radar_data]
        values = [item[1] for item in radar_data]
        actual_values = [item[2] for item in radar_data]
        
        # 创建雷达图
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='综合评分',
            line_color='#3b82f6',
            fillcolor='rgba(59, 130, 246, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor='#e5e7eb'
                ),
                angularaxis=dict(
                    gridcolor='#e5e7eb'
                )
            ),
            showlegend=False,
            height=400,
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示具体数值 - 改为两列布局
        col1, col2 = st.columns(2)
        
        # 第一列：德育、智育、附加分
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-weight: 600; color: #374151; margin-bottom: 0.25rem;">第一学年德育</div>
                <div style="color: #3b82f6; font-weight: bold; font-size: 1.2rem;">{format_value(student_data.get('第一学年德育', student_data.get('德育')))}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-weight: 600; color: #374151; margin-bottom: 0.25rem;">第一学年智育</div>
                <div style="color: #3b82f6; font-weight: bold; font-size: 1.2rem;">{format_value(student_data.get('第一学年智育', student_data.get('智育')))}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-weight: 600; color: #374151; margin-bottom: 0.25rem;">第一学年附加分</div>
                <div style="color: #3b82f6; font-weight: bold; font-size: 1.2rem;">{format_value(student_data.get('第一学年附加分', student_data.get('附加分', student_data.get('23-24附加分'))))}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 第二列：体测成绩、体测等级、综测总分
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-weight: 600; color: #374151; margin-bottom: 0.25rem;">第一学年体测成绩</div>
                <div style="color: #3b82f6; font-weight: bold; font-size: 1.2rem;">{format_value(student_data.get('第一学年体测成绩', student_data.get('体测成绩')))}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-weight: 600; color: #374151; margin-bottom: 0.25rem;">第一学年体测等级</div>
                <div style="color: #3b82f6; font-weight: bold; font-size: 1.2rem;">{format_value(student_data.get('第一学年体测评级', student_data.get('体测等级')))}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-weight: 600; color: #374151; margin-bottom: 0.25rem;">第一学年综测总分</div>
                <div style="color: #3b82f6; font-weight: bold; font-size: 1.2rem;">{format_value(student_data.get('第一学年综测总分', student_data.get('第一学年总分', student_data.get('测评总分'))))}</div>
            </div>
            """, unsafe_allow_html=True)

        # 添加归一化细则说明
        with st.expander("ℹ️ 雷达图评分归一化细则", expanded=False):
            st.markdown("""
            雷达图中的各项评分均已通过以下方式进行归一化处理，以便在统一的0-100范围内进行比较：
            **各维度具体归一化参数 (预设最小值 / 预设最大值)：**
            *   `第一学年德育`: 12 / 15
            *   `第一学年智育`: 50 / 100
            *   `第一学年体测`: 60 / 120
            *   `第一学年附加分`: -1 / 6
            *   `第一学年总分`: 50 / 110
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 学期成绩趋势图
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📈 学业成绩分析")
        
        # 准备绩点数据
        gpa_data = []
        for semester in ['第一学期绩点', '第二学期绩点', '第三学期绩点']:
            value = student_data.get(semester)
            if pd.notna(value) and value is not None:
                try:
                    float_value = float(value)
                    gpa_data.append({
                        'semester': semester.replace('绩点', ''),
                        'gpa': float_value
                    })
                except (ValueError, TypeError):
                    continue
        
        if gpa_data:
            semesters = [item['semester'] for item in gpa_data]
            gpas = [item['gpa'] for item in gpa_data]
            
            # 创建折线图
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=semesters,
                y=gpas,
                mode='lines+markers',
                name='绩点',
                line=dict(color='#8b5cf6', width=3),
                marker=dict(size=8, color='#8b5cf6')
            ))
            
            fig.update_layout(
                xaxis_title="学期",
                yaxis_title="绩点",
                yaxis=dict(range=[0, 4]),
                height=300,
                margin=dict(t=30, b=30, l=30, r=30),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 显示平均绩点
            avg_gpa = sum(gpas) / len(gpas)
            cols = st.columns(len(gpa_data))
            for i, data in enumerate(gpa_data):
                with cols[i]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="font-weight: 600; color: #374151; margin-bottom: 0.25rem;">{data['semester']}</div>
                        <div style="color: #8b5cf6; font-weight: bold; font-size: 1.5rem;">{data['gpa']:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("📊 暂无绩点数据")
        
        study_items = [
            ("是否过四级", student_data.get('是否过四级', student_data.get('四级成绩'))),
            ("是否过六级", student_data.get('是否过六级', student_data.get('六级成绩'))),
            ("挂科次数", student_data.get('挂科')),
            ("所获学分", student_data.get('所获学分'))
        ]
        
        for label, raw_value in study_items:
            value = format_value(raw_value)
            
            # 根据不同情况设置样式
            if label.startswith("挂科"):
                status_class = "status-help" if value != '无' and value != '0' else "status-none"
            elif label == "所获学分":
                status_class = "status-scholarship" if value != '无' else "status-none"
            elif label.startswith("是否过"):
                # 四级六级通过显示绿色，未通过显示红色
                try:
                    # 尝试将值转换为数字，如果是分数的话
                    num_value = float(value) if value != '无' else 0
                    # 四级成绩大于425分，六级成绩大于425分视为通过
                    status_class = "status-no-help" if num_value >= 425 else "status-help"
                except (ValueError, TypeError):
                    # 如果不是数字，则按字符串判断
                    status_class = "status-no-help" if value != '无' and value.lower() in ['是', 'yes', 'true', '1', 'pass', '通过'] else "status-help"
            else:
                status_class = "status-scholarship" if value != '无' and value.lower() not in ['否', 'no', 'false', '0'] else "status-help"
            
            st.markdown(f"""
            <div style="background: #f8fafc; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #6b7280;">{label}：</span>
                    <span class="status-badge {status_class}">{value}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        
        
    else:
        st.warning("🔍 未找到匹配的学生，请调整搜索条件")