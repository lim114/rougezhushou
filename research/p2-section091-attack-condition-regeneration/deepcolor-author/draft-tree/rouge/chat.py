"""Provider-neutral streamed chat. No credentials are logged or persisted here."""
import json
from dataclasses import dataclass
from urllib.parse import urlsplit
import httpx

@dataclass(frozen=True)
class ProviderConfig:
    base_url: str
    model: str
    protocol: str = 'chat_completions'
    timeout: float = 60

def stream_chat(config, messages, api_key, cancellation):
    url = urlsplit(config.base_url)
    if url.username or url.password or url.query or url.fragment:
        raise ValueError('服务地址不能包含凭据、查询参数或片段。')
    if url.scheme != 'https' and not (url.scheme == 'http' and url.hostname in ('localhost','127.0.0.1','::1')):
        raise ValueError('服务地址需要 HTTPS，本机测试地址可使用 HTTP。')
    if not config.model.strip():
        raise ValueError('请填写服务商提供的模型标识。')
    if config.protocol not in ('chat_completions', 'responses'):
        raise ValueError('协议尚未实现。')
    if cancellation.is_set():
        return
    headers = {'Accept': 'text/event-stream'}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'
    body = {'model': config.model, 'messages' if config.protocol == 'chat_completions' else 'input': messages, 'stream': True}
    endpoint = '/chat/completions' if config.protocol == 'chat_completions' else '/responses'
    try:
        with httpx.Client(timeout=config.timeout, trust_env=False, follow_redirects=False) as client:
            with client.stream('POST', config.base_url.rstrip('/') + endpoint, json=body, headers=headers) as response:
                if response.status_code != 200:
                    raise RuntimeError(f'服务返回 HTTP {response.status_code}，请核对地址、模型及凭据。')
                for line in response.iter_lines():
                    if cancellation.is_set():
                        return
                    if not line.startswith('data:'):
                        continue
                    data = line[5:].strip()
                    if data == '[DONE]':
                        return
                    event = json.loads(data)
                    if 'error' in event:
                        raise RuntimeError('服务返回生成错误。')
                    if config.protocol == 'responses':
                        if event.get('type') == 'response.completed':
                            return
                        if event.get('type') in ('response.failed', 'response.incomplete', 'error'):
                            raise RuntimeError('服务生成失败或未完成。')
                        if event.get('type') == 'response.output_text.delta':
                            yield event['delta']
                        continue
                    for choice in event.get('choices', []):
                        content = choice.get('delta', {}).get('content')
                        if content:
                            yield content
                if not cancellation.is_set():
                    raise ConnectionError('回答流在完成标记之前中断；保留的内容是未完成回答。')
    except httpx.TimeoutException:
        raise TimeoutError('服务响应超时。') from None
    except httpx.HTTPError:
        raise ConnectionError('网络连接失败；请检查服务地址及网络。') from None
