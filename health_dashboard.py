from datetime import date
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from plotly.subplots import make_subplots

# エクセルの読み込み
df = pd.read_excel("health_data.xlsx", sheet_name="Sheet1", header=1)
df = df.dropna()

# 日付のデータ型変換
df["日付"] = pd.to_datetime(df["日付"])

# Streamlitのページ設定
st.set_page_config(
    page_title="健康管理ダッシュボード",
    layout="wide",
)

# 現在の年月を取得
today = date.today()
this_year = today.year
this_month = today.month

st.title(f"{this_year}年{this_month}月")

# 4カラム表示
col1, col2, col3, col4 = st.columns(4)

# 今年のデータ
this_year_data = df[df["日付"].dt.year == this_year]

# 最新の日付を取得
latest_date = this_year_data["日付"].max()

# 最新の日付の目標体重と現在の体重を取得
latest_weight_data = this_year_data[this_year_data["日付"] == latest_date]
latest_target_weight = latest_weight_data["目標体重"].values[0]
latest_weight = latest_weight_data["体重"].values[0]
weight_diff = latest_target_weight - latest_weight

# 今年の各項目の最高値を移動距離の最高値に変更
this_year_data["腕立て"] = this_year_data["腕立て"].apply(lambda x: int(x) if x != "-" else 0)
this_year_data["腹筋"] = this_year_data["腹筋"].apply(lambda x: int(x) if x != "-" else 0)
this_year_data["背筋"] = this_year_data["背筋"].apply(lambda x: int(x) if x != "-" else 0)
this_year_data["スクワット"] = this_year_data["スクワット"].apply(lambda x: int(x) if x != "-" else 0)
this_year_data["運動回数"] = this_year_data[["腕立て", "腹筋", "背筋", "スクワット"]].max(axis=1)

# 今年の合計移動距離
this_year_data["移動距離"] = this_year_data["移動距離"].apply(lambda x: float(x) if x != "-" else 0)

# 今年の移動距離差
this_year_data["移動距離差"] = this_year_data["目標移動距離"] - this_year_data["移動距離"]

# 記録日数
this_year_counts = this_year_data["日付"].count()
col1.metric("記録日数", f"{this_year_counts}日")
# 目標体重と現在の体重の差
col2.metric("目標体重までの差", f"{weight_diff:.1f}kg")
# 移動距離の最高値 (移動距離の最高値)
this_year_exercise_count = this_year_data["移動距離"].max()
col3.metric("移動距離の最高値", f"{this_year_exercise_count:.1f}km")
# 合計移動距離
this_year_distance_diff = this_year_data["移動距離"].sum()
col4.metric("合計移動距離", f"{this_year_distance_diff:.1f}km")

# 3つのグラフを均等の横幅で表示
col1, col2, col3 = st.columns(3)

# 月別の目標移動距離の推移
monthly_target_distance_df = this_year_data.groupby(this_year_data['日付'].dt.to_period('M')).agg({
    '目標移動距離': 'max'
}).reset_index()

# 月別の運動回数の推移
monthly_exercise_count_df = this_year_data.groupby(this_year_data['日付'].dt.to_period('M')).agg({
    '運動回数': 'max'
}).reset_index()

# 月別の移動距離差の推移
monthly_distance_diff_df = this_year_data.groupby(this_year_data['日付'].dt.to_period('M')).agg({
    '移動距離': 'sum'
}).reset_index()

# Period型を文字列に変換
monthly_target_distance_df['日付'] = monthly_target_distance_df['日付'].dt.strftime('%Y-%m')
monthly_exercise_count_df['日付'] = monthly_exercise_count_df['日付'].dt.strftime('%Y-%m')
monthly_distance_diff_df['日付'] = monthly_distance_diff_df['日付'].dt.strftime('%Y-%m')

# 目標達成率を計算し、新しいカラム '達成率' をデータフレームに追加
monthly_target_distance_df['達成率'] = (1 - (monthly_distance_diff_df['移動距離'] / monthly_target_distance_df['目標移動距離'])) * 100

# 3つのグラフを均等の横幅で表示
col1, col2, col3 = st.columns(3)

# 月ごとの達成率を計算
monthly_target_distance_df['達成率'] = (1 - (monthly_distance_diff_df['移動距離'] / monthly_target_distance_df['目標移動距離'])) * 100

# 達成率が100%を超える場合、100%に制限
monthly_target_distance_df['達成率'] = monthly_target_distance_df['達成率'].clip(upper=100)

# 月ごとの目標移動距離と達成率の推移
fig1 = make_subplots(specs=[[{"secondary_y": True}]])
fig1.add_trace(go.Scatter(x=monthly_target_distance_df['日付'], y=monthly_target_distance_df['目標移動距離'], name="目標移動距離"), secondary_y=False)
fig1.add_trace(go.Scatter(x=monthly_target_distance_df['日付'], y=monthly_target_distance_df['達成率'], name="達成率", line=dict(dash='dot')), secondary_y=True)
fig1.update_xaxes(title_text="日付")
fig1.update_yaxes(title_text="目標移動距離", secondary_y=False)
fig1.update_yaxes(title_text="達成率 (%)", secondary_y=True)
fig1.update_layout(title="月別目標移動距離と達成率")
col1.plotly_chart(fig1, use_container_width=True)


# 月ごとの運動回数の推移
fig2 = px.line(monthly_exercise_count_df, x="日付", y="運動回数", title="月別運動回数")
col2.plotly_chart(fig2, use_container_width=True)

# 月ごとの移動距離差の推移
fig3 = px.line(monthly_distance_diff_df, x="日付", y="移動距離", title="月別移動距離")
fig3.update_yaxes(title_text="移動距離", secondary_y=False)
col3.plotly_chart(fig3, use_container_width=True)


# 詳細表示
with st.expander("詳細データ", expanded=True):
    # 表示する期間の入力
    min_date = this_year_data["日付"].min().date()
    max_date = this_year_data["日付"].max().date()

    # 開始日と終了日のスライダーウィジェットを追加
    selected_start_date, selected_end_date = st.slider(
        "表示する期間を選択",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date)
    )

    # 運動項目の選択
    exercises = ["腕立て", "腹筋", "背筋", "スクワット"]
    selected_exercises = st.multiselect(
        "表示する運動項目を選択",
        exercises,
        default=exercises
    )

    # 選択した日付範囲と運動項目に対する折れ線グラフを作成
    filtered_data = this_year_data[
        (this_year_data["日付"].dt.date >= selected_start_date) &
        (this_year_data["日付"].dt.date <= selected_end_date)
    ]

    if not filtered_data.empty:
        fig = px.line(
            filtered_data,
            x="日付",
            y=selected_exercises,
            title=f"選択した運動項目の推移 ({selected_start_date} ～ {selected_end_date})"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("選択した条件に該当するデータがありません。")

    # 移動距離の推移の折れ線グラフを作成
    distance_data = filtered_data[["日付", "移動距離"]]
    fig5 = px.line(
        distance_data,
        x="日付",
        y="移動距離",
        title=f"移動距離の推移 ({selected_start_date} ～ {selected_end_date})"
    )
    st.plotly_chart(fig5, use_container_width=True)

    # 選択した運動項目と常に移動距離のデータテーブルを表示
    selected_exercises = ["移動距離"] + selected_exercises  # 移動距離を選択した運動項目に追加
    filtered_data_table = filtered_data[["日付"] + selected_exercises]

    # 選択した運動項目と移動距離のデータを取得
    selected_data = filtered_data_table[selected_exercises + ["移動距離"]]

    # データを正規化
    scaler = StandardScaler()
    normalized_data = scaler.fit_transform(selected_data)

    # 正規化後のデータを新しいDataFrameに格納
    normalized_df = pd.DataFrame(normalized_data, columns=selected_data.columns, index=filtered_data_table.index)

    # ヒートマップの作成
    fig = go.Figure(data=go.Heatmap(
        z=normalized_df.corr().values,  # 正規化後の相関係数を表示
        x=normalized_df.columns,
        y=normalized_df.columns,
        colorscale='RdBu'
    ))

    fig.update_xaxes(side="top")
    fig.update_layout(width=800, height=500, xaxis_title="運動項目", yaxis_title="運動項目")

    st.write("選択した運動項目と常に移動距離の正規化相関係数ヒートマップ")
    st.plotly_chart(fig, use_container_width=True)

    # テーブルの表示
    st.write("選択した運動項目と常に移動距離のデータセット")
    st.dataframe(filtered_data_table, use_container_width=True)
