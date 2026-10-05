#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""蝉镜 AI 开放平台客户端（标准库实现，无第三方依赖）。

封装：access_token 获取与本地缓存、公共音色/数字人列表、
语音合成任务、数字人视频合成任务，及规定退避节奏的轮询。

业务成功以响应体 code === 0 为准（HTTP 200 不代表成功）。
凭证只从服务端环境变量或 tools/.chanjing.env 读取；
secret 与 token 不进入日志，token 缓存在 tools/.chanjing-state.json。

接口基础地址：https://open-api.chanjing.cc/open/v1
文档：https://doc.chanjing.cc/
"""

import io
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(HERE, '.chanjing.env')
STATE_FILE = os.path.join(HERE, '.chanjing-state.json')
BASE_URL = 'https://open-api.chanjing.cc/open/v1'

HTTP_TIMEOUT_S = 30      # 单次 HTTP 请求超时
TOKEN_REFRESH_MARGIN = 60  # token 提前 60 秒刷新

# 轮询节奏（任务约定）
TTS_FIRST_DELAY = 3
TTS_MAX_DELAY = 10
TTS_TOTAL_TIMEOUT = 300
VIDEO_FIRST_DELAY = 5
VIDEO_MAX_DELAY = 15
VIDEO_TOTAL_TIMEOUT = 1200


class ChanjingError(RuntimeError):
    """接口业务失败。保留 code、msg、trace_id、接口路径。"""

    def __init__(self, path, code, msg, trace_id, extra=None):
        self.path = path
        self.code = code
        self.msg = msg
        self.trace_id = trace_id
        self.extra = extra or {}
        super(ChanjingError, self).__init__(
            '蝉镜接口失败 %s code=%s msg=%s trace_id=%s'
            % (path, code, msg, trace_id))


def load_credentials():
    """从环境变量与 tools/.chanjing.env 读凭证。返回 (app_id, secret)。
    只返回值，不打印；缺失时抛错。"""
    env = dict(os.environ)
    if os.path.exists(ENV_FILE):
        with io.open(ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or '=' not in line:
                    continue
                k, v = line.split('=', 1)
                env.setdefault(k.strip(), v.strip())
    app_id = env.get('CHANJING_APP_ID', '').strip()
    secret = env.get('CHANJING_SECRET_KEY', '').strip()
    if not app_id or not secret:
        raise RuntimeError(
            '缺少凭证：请在服务端环境变量或 tools/.chanjing.env 中配置 '
            'CHANJING_APP_ID / CHANJING_SECRET_KEY')
    return app_id, secret


def _http_json(method, url, body=None, token=None):
    """发起 HTTPS 请求并解析 JSON。TLS 走系统默认校验，不关闭。
    HTTP 错误也尝试解析响应体（业务 code 在 body 里）。"""
    data = json.dumps(body).encode('utf-8') if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Content-Type', 'application/json')
    if token:
        req.add_header('access_token', token)
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_S) as resp:
            raw = resp.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        raw = e.read().decode('utf-8', 'replace')
    try:
        return json.loads(raw)
    except ValueError:
        raise RuntimeError('接口返回非 JSON：%s -> %s' % (url, raw[:200]))


def _load_token_state():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(io.open(STATE_FILE, encoding='utf-8'))
        except ValueError:
            pass
    return {}


def _save_token_state(token, expire_in):
    with io.open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump({'access_token': token, 'expire_in': expire_in,
                   'fetched_at': int(time.time())}, f)


def get_access_token(force=False):
    """返回有效 access_token；按 expire_in 缓存并提前刷新。"""
    if not force:
        st = _load_token_state()
        token = st.get('access_token')
        if token and st.get('fetched_at') and st.get('expire_in'):
            age = int(time.time()) - st['fetched_at']
            if age < st['expire_in'] - TOKEN_REFRESH_MARGIN:
                return token
    app_id, secret = load_credentials()
    payload = _http_json('POST', '%s/access_token' % BASE_URL,
                         {'app_id': app_id, 'secret_key': secret})
    if payload.get('code') != 0:
        raise ChanjingError('/access_token', payload.get('code'),
                           payload.get('msg'), payload.get('trace_id'))
    data = payload.get('data') or {}
    token = data.get('access_token')
    expire_in = int(data.get('expire_in') or 0)
    if not token or expire_in <= 0:
        raise RuntimeError('access_token 响应缺少 token 或 expire_in')
    _save_token_state(token, expire_in)
    return token


def call(method, path, body=None, query=None):
    """调用业务接口；code !== 0 抛 ChanjingError。返回 data。"""
    url = BASE_URL + path
    if query:
        url += '?' + urllib.parse.urlencode(query)
    token = get_access_token()
    payload = _http_json(method, url, body=body, token=token)
    if payload.get('code') != 0:
        raise ChanjingError(path, payload.get('code'), payload.get('msg'),
                           payload.get('trace_id'), extra=payload.get('data'))
    return payload.get('data'), payload.get('trace_id')


# --- 业务接口 ---

def list_common_audio(page=1, size=20):
    return call('GET', '/list_common_audio',
                query={'page': page, 'size': size})


def list_common_dp(page=1, size=20):
    return call('GET', '/list_common_dp',
                query={'page': page, 'size': size})


def create_audio_task(audio_man, text, speed=1):
    """创建 TTS 任务，返回 task_id。
    text 为原文本；同时填富文本 text 与 plain_text。"""
    body = {
        'audio_man': audio_man,
        'speed': speed,
        'text': {'text': text, 'plain_text': text},
    }
    data, _ = call('POST', '/create_audio_task', body)
    return (data or {}).get('task_id')


def audio_task_state(task_id):
    data, trace_id = call('POST', '/audio_task_state', {'task_id': task_id})
    return data, trace_id


def create_video(payload):
    """提交数字人视频合成。返回任务 ID（data 为字符串本身）。"""
    data, _ = call('POST', '/create_video', payload)
    if not isinstance(data, str) or not data:
        raise RuntimeError('create_video 响应 data 非任务 ID 字符串：%r' % type(data))
    return data


def get_video(task_id):
    return call('GET', '/video', query={'id': task_id})


# --- 轮询 ---

def wait_audio(task_id):
    """TTS 轮询：首间隔 3 秒、指数退避上限 10 秒、总超时 5 分钟。
    成功 status===9 且 full.url 非空；errMsg/errReason 非空立即失败。
    超时抛出最后状态。"""
    start = time.time()
    delay = TTS_FIRST_DELAY
    n = 0
    last = None
    while time.time() - start < TTS_TOTAL_TIMEOUT:
        time.sleep(delay)
        last, trace_id = audio_task_state(task_id)
        full = last.get('full') or {}
        if last.get('status') == 9 and full.get('url'):
            return last, trace_id
        if last.get('errMsg') or last.get('errReason'):
            raise ChanjingError(
                '/audio_task_state', None,
                'TTS 失败 errMsg=%s errReason=%s'
                % (last.get('errMsg'), last.get('errReason')), trace_id)
        n += 1
        delay = min(TTS_MAX_DELAY, TTS_FIRST_DELAY * (2 ** n))
    raise RuntimeError(
        'TTS 轮询超时：最后 status=%s errMsg=%s errReason=%s trace_id=%s'
        % ((last or {}).get('status'), (last or {}).get('errMsg'),
           (last or {}).get('errReason'), trace_id))


def wait_video(task_id):
    """视频轮询：首间隔 5 秒、指数退避上限 15 秒、总超时 20 分钟。
    completed 且 video_url 非空成功；failed 报 msg；other 立即失败。"""
    start = time.time()
    delay = VIDEO_FIRST_DELAY
    n = 0
    while True:
        time.sleep(delay)
        data, trace_id = get_video(task_id)
        qs = data.get('queue_status')
        if qs == 'completed' and data.get('video_url'):
            return data, trace_id
        if qs == 'failed':
            raise ChanjingError('/video', None,
                               '视频合成失败 msg=%s' % data.get('msg'),
                               trace_id)
        if qs == 'other':
            raise ChanjingError(
                '/video', None,
                '队列状态 other queue_status=%s msg=%s queue_desc=%s'
                % (qs, data.get('msg'), data.get('queue_desc')), trace_id)
        if time.time() - start >= VIDEO_TOTAL_TIMEOUT:
            raise RuntimeError(
                '视频轮询超时：最后 queue_status=%s msg=%s queue_desc=%s trace_id=%s'
                % (qs, data.get('msg'), data.get('queue_desc'), trace_id))
        n += 1
        delay = min(VIDEO_MAX_DELAY, VIDEO_FIRST_DELAY * (2 ** n))
