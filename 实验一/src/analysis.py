"""Pure CSV validation and brand aggregation, independent of the web UI."""

import csv
import io
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

REQUIRED_FIELDS = ("brand", "price", "rating")


class DataError(ValueError):
    """A CSV cannot be analysed; the message is suitable for display."""


def analyse_csv(raw: bytes) -> dict:
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DataError("CSV 编码错误：请保存为 UTF-8 编码后重试。") from exc

    try:
        reader = csv.DictReader(io.StringIO(text, newline=""))
        if not reader.fieldnames:
            raise DataError("CSV 为空：请提供包含表头的数据文件。")
        fields = [field.strip() if field is not None else "" for field in reader.fieldnames]
        missing = [field for field in REQUIRED_FIELDS if field not in fields]
        if missing:
            raise DataError("CSV 缺少必需字段：" + "、".join(missing) + "。需要 brand、price、rating。")
        if len(fields) != len(set(fields)):
            raise DataError("CSV 表头有重复字段，请修改后重试。")
        reader.fieldnames = fields

        groups: dict[str, dict] = {}
        warnings: list[str] = []
        total_rows = 0
        valid_rows = 0
        for row_number, row in enumerate(reader, start=2):
            if row_number > 100002:
                raise DataError("CSV 超过 100000 行，请拆分文件后重试。")
            if None in row:
                warnings.append(f"第 {row_number} 行列数超过表头，已跳过。")
                total_rows += 1
                continue
            if not any(str(value or "").strip() for value in row.values()):
                continue
            total_rows += 1
            brand = (row.get("brand") or "").strip()
            price_text = (row.get("price") or "").strip()
            rating_text = (row.get("rating") or "").strip()
            if not brand or not price_text or not rating_text:
                warnings.append(f"第 {row_number} 行 brand、price 或 rating 为空，已跳过。")
                continue
            try:
                price = Decimal(price_text)
                rating = Decimal(rating_text)
            except InvalidOperation:
                warnings.append(f"第 {row_number} 行价格或评分不是数字，已跳过。")
                continue
            if not price.is_finite() or not rating.is_finite() or price < 0:
                warnings.append(f"第 {row_number} 行价格或评分无效，已跳过。")
                continue
            group = groups.setdefault(brand, {"count": 0, "price_sum": Decimal(0), "rating_sum": Decimal(0)})
            group["count"] += 1
            group["price_sum"] += price
            group["rating_sum"] += rating
            valid_rows += 1
    except csv.Error as exc:
        raise DataError(f"CSV 格式错误：{exc}") from exc

    if not groups:
        raise DataError("没有可分析的数据：请检查 brand、price、rating 是否有非空有效值。")

    def rounded(value: Decimal) -> float:
        return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    result = [
        {"brand": brand, "count": group["count"],
         "average_price": rounded(group["price_sum"] / group["count"]),
         "average_rating": rounded(group["rating_sum"] / group["count"])}
        for brand, group in sorted(groups.items(), key=lambda item: item[0].casefold())
    ]
    return {"required_fields": list(REQUIRED_FIELDS), "total_rows": total_rows,
            "valid_rows": valid_rows, "skipped_rows": total_rows - valid_rows,
            "brands": result, "warnings": warnings}
