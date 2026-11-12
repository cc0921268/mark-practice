"""Rebuild deterministic course demonstration artifacts within this project."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src import system

ROOT = system.ROOT


def main() -> None:
    (ROOT / "data/sample").mkdir(parents=True, exist_ok=True)
    (ROOT / "outputs").mkdir(exist_ok=True)
    feedback_a = ["参数信息不够直观", "想看真实续航", "佩戴演示有帮助", "价格需要说明",
                  "希望看到降噪条件", "想看充电时间", "页面重点不清", "想看耳塞尺寸",
                  "音质描述太笼统", "配送说明不够", "希望看到对照", "需注明测试环境"]
    feedback_b = ["佩戴步骤清楚", "想看不同耳型", "对照形式容易理解", "续航测试条件清楚",
                  "希望添加价格信息", "适配说明有用", "还想看实测视频", "需要保修说明",
                  "连接场景具体", "购买入口不明显", "降噪边界说明好", "还需更多样本"]
    rows = []
    for i in range(12):
        rows.append({"respondent_id": f"SIM-A-{i+1:02d}", "variant": "A",
                     "click_intent": [2,3,3,4,2,3,4,3,2,3,4,3][i],
                     "purchase_intent": [2,2,3,3,2,3,3,2,3,2,4,3][i],
                     "feedback": feedback_a[i], "data_status": "SIMULATED"})
        rows.append({"respondent_id": f"SIM-B-{i+1:02d}", "variant": "B",
                     "click_intent": [4,4,5,3,4,4,5,4,3,4,4,5][i],
                     "purchase_intent": [3,4,4,3,4,3,4,4,3,3,4,4][i],
                     "feedback": feedback_b[i], "data_status": "SIMULATED"})
    sample = pd.DataFrame(rows)
    sample.to_csv(ROOT / "data/sample/ab_simulated.csv", index=False, encoding="utf-8-sig")
    table, meta = system.analyze_ab(sample)
    table.to_csv(ROOT / "outputs/ab_summary_simulated.csv", index=False, encoding="utf-8-sig")
    (ROOT / "outputs/ab_summary_simulated.json").write_text(
        json.dumps({**meta, "simulation": True, "results": table.to_dict("records")}, ensure_ascii=False, indent=2), encoding="utf-8")

    products = system.load_products()
    encoded, _ = system.load_encoded()
    result = system.analyze(products, encoded, "Skullcandy")
    for section, items in result.items():
        for key, value in items.items():
            if isinstance(value, pd.DataFrame):
                value.to_csv(ROOT / "outputs" / f"{section}_{key}.csv", index=False, encoding="utf-8-sig")
            elif key == "briefs":
                (ROOT / "outputs/strategy_briefs.json").write_text(
                    json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    system.init_db()
    system.save_profile("Skullcandy", "关注佩戴舒适度与连接稳定性的蓝牙耳机用户",
                        "课程研究对象；资料来自项目内商品与评论样本。")
    print("演练数据与分析表已生成。")


if __name__ == "__main__":
    main()

