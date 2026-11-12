"""Deterministic local HTTP stand-in for the model portion of the workflow."""

import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread


def mock_result(step: str, context: dict) -> dict:
    briefs = context.get("briefs", [])
    top = briefs[0] if briefs else {}
    theme = top.get("theme", "device_failure")
    user_ids = top.get("user_evidence_ids", [])[:3]
    listing_ids = top.get("competitor_checked_listing_ids", [])[:3]
    if step == "target_consumer":
        return {"segment": "曾遇到单耳停用或充电困扰、希望先了解适用条件的耳机使用者",
                "why": "优先响应已出现的可靠性与充电反馈；样本不是总体人群画像。",
                "evidence_ids": user_ids, "status": "hypothesis"}
    if step == "communication_theme":
        return {"theme": "先讲清测试条件，再讨论耳机可靠性",
                "message": "用实测条件说明单耳使用与充电排查步骤。",
                "source_theme": theme, "evidence_ids": user_ids,
                "competitor_listing_ids": listing_ids, "status": "draft"}
    if step == "channel_plan":
        return {"channels": [
            {"name": "产品详情页", "role": "展示测试条件与保修边界", "metric": "说明模块点击人数/详情页访问人数"},
            {"name": "短视频", "role": "演示可复核的单耳与充电排查步骤", "metric": "完整观看人数/视频曝光人数"},
            {"name": "售后知识页", "role": "帮助已遇到问题的使用者定位排查路径", "metric": "完成排查人数/知识页访问人数"}],
                "evidence_ids": user_ids, "status": "draft"}
    if step == "campaign":
        return {"name": "清波 ClearWave 蓝牙耳机新品推广草案",
                "objective": "验证可靠性说明是否帮助用户理解产品适用条件",
                "audience": context.get("target_consumer", {}).get("segment", "未知"),
                "theme": context.get("communication_theme", {}).get("theme", "未知"),
                "channels": context.get("channel_plan", {}).get("channels", []),
                "evidence_ids": user_ids, "competitor_listing_ids": listing_ids,
                "metric": "说明模块点击人数/详情页访问人数；基线待收集",
                "claim_boundary": "仅为课程策划草案；产品性能必须经实测，不能宣称已解决全部故障。",
                "approval_status": "pending_human_review"}
    raise ValueError(f"unknown step: {step}")


class MockHandler(BaseHTTPRequestHandler):
    injections: dict[str, str] = {}
    request_counts: dict[str, int] = {}

    def do_POST(self):
        if self.path != "/model":
            self.send_error(404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 1 <= size <= 1_000_000:
                self.send_error(413)
                return
            payload = json.loads(self.rfile.read(size))
            step = payload["step"]
            context = payload.get("context", {})
            self.request_counts[step] = self.request_counts.get(step, 0) + 1
            mode = self.injections.get(step)
            if mode == "http_503_once" and self.request_counts[step] == 1:
                self.send_error(503, "simulated outage")
                return
            if mode == "http_503":
                self.send_error(503, "simulated outage")
                return
            if mode == "timeout":
                time.sleep(0.4)
            if mode == "invalid_json":
                body = b"{invalid json"
            elif mode == "missing_field":
                body = json.dumps({"result": {"status": "draft"}}).encode("utf-8")
            else:
                body = json.dumps({"result": mock_result(step, context)}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass
        except (KeyError, ValueError, json.JSONDecodeError):
            self.send_error(400)

    def log_message(self, *_args):
        pass


def start_mock(injections: dict[str, str] | None = None):
    handler = type("RunMockHandler", (MockHandler,), {
        "injections": dict(injections or {}), "request_counts": {}})
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_port}/model"

