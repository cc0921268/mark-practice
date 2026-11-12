"""Optional browser acceptance test; run via the GitHub webapp-testing helper."""

from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8501"


def upload(page, name: str) -> None:
    page.locator("#csv-file").set_input_files(str(ROOT / "data" / "sample" / name))
    page.locator("#data-source").fill("课程自建测试样例")
    page.locator("#collection-date").fill("2026-11-10")
    page.get_by_role("button", name="上传并分析").click()


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1365, "height": 1000}, device_scale_factor=1)
    page.goto(BASE)
    page.wait_for_load_state("networkidle")
    assert page.get_by_role("heading", name="营销数据分析").is_visible()

    upload(page, "normal.csv")
    page.get_by_text("上传成功，分析结果已生成。").wait_for()
    assert page.locator("#result-table tr").count() == 2
    assert "150.00" in page.locator("#result-table").inner_text()
    page.screenshot(path=str(ROOT / "outputs" / "running_screenshot.png"), full_page=True)

    page.locator("#brand-filter").select_option(label="星河")
    assert page.locator("#result-table tr").count() == 1
    assert "星河" in page.locator("#result-table").inner_text()
    page.locator("#brand-filter").select_option("")
    assert page.locator("#result-table tr").count() == 2

    upload(page, "missing_field.csv")
    page.get_by_text("CSV 缺少必需字段：rating", exact=False).wait_for()
    assert page.locator("#results").is_hidden()

    upload(page, "empty_values.csv")
    page.get_by_text("上传成功，分析结果已生成。").wait_for()
    assert page.locator("#valid-count").inner_text() == "2"
    assert page.locator("#skipped-count").inner_text() == "3"
    assert "第 3 行" in page.locator("#warnings").inner_text()
    browser.close()
print("Browser acceptance: normal upload, chart/table, filter, missing field, empty values OK")
