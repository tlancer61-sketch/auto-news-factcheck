#!/usr/bin/env python3
"""Render an evidence summary as offline HTML. Does not verify factual truth."""
import argparse
import html
import json
from pathlib import Path
from urllib.parse import urlsplit

STATUSES = {'已核实', '有限支持', '存在争议', '无法核实', '与证据不符'}

def esc(value):
    return html.escape(str(value), quote=True)

def render(d):
    for key in ('title', 'as_of', 'scope', 'summary', 'revision'):
        if not isinstance(d.get(key), str) or not d[key].strip():
            raise ValueError(f'{key} 必须是非空字符串')
    for key in ('timeline', 'claims', 'parties', 'laws', 'statements', 'unknowns', 'sources'):
        if not isinstance(d.get(key), list):
            raise ValueError(f'{key} 必须是数组')
    ids = [s['id'] for s in d['sources']]
    if len(set(ids)) != len(ids):
        raise ValueError('来源ID重复')
    anchors = {sid: f'source-{i}' for i, sid in enumerate(ids)}
    def refs(item):
        result = []
        for sid in item.get('sources', []):
            if sid not in anchors:
                raise ValueError(f'引用不存在的来源 {sid}')
            result.append(f'<a href="#{anchors[sid]}">{esc(sid)}</a>')
        return '<p class="refs">来源：' + (' · '.join(result) or '无可用来源，待核实') + '</p>'
    def section(title, items):
        return f'<section><h2>{title}</h2>' + (''.join(items) or '<p class="muted">无相关材料；适用性及缺口见未知清单。</p>') + '</section>'
    blocks = []
    blocks.append(section('01 / 事件时间线', [f'<article class="timeline"><b>{esc(t["time"])}</b><p>{esc(t["text"])}</p>{refs(t)}</article>' for t in d['timeline']]))
    claims = []
    for c in d['claims']:
        status = c['status']
        if status not in STATUSES:
            raise ValueError(f'未知核查状态 {status}')
        claims.append(f'<article><span class="badge">{esc(status)}</span><h3>{esc(c["id"])} · {esc(c["text"])}</h3><p>{esc(c["analysis"])}</p>{refs(c)}</article>')
    blocks.append(section('02 / 逐条核查', claims))
    for key, title in [('parties', '03 / 各方说法'), ('laws', '04 / 法规与适用边界')]:
        blocks.append(section(title, [f'<article><h3>{esc(x["name"])}</h3><p>{esc(x["text"])}</p>{refs(x)}</article>' for x in d[key]]))
    if d.get('judgments'):
        blocks.append(section('判断与处理路线｜条件分析', [f'<article><h3>{esc(x["name"])}</h3><p>{esc(x["text"])}</p>{refs(x)}</article>' for x in d['judgments']]))
    statements = []
    for s in d['statements']:
        panels = ''.join(f'<div><h3>{label}</h3><p>{esc(s[key])}</p></div>' for key, label in [('official', '官方角度'), ('social', '社会与消费者角度'), ('language', '语言文法角度')])
        statements.append(f'<article><blockquote>{esc(s["quote"])}</blockquote><div class="columns">{panels}</div>{refs(s)}</article>')
    blocks.append(section('05 / 声明三层解读', statements))
    blocks.append(section('06 / 仍然不知道什么', [f'<article class="unknown">{esc(x)}</article>' for x in d['unknowns']]))
    sources = []
    for s in d['sources']:
        url = s.get('url', '')
        parsed = urlsplit(url)
        link = f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">阅读原文</a>' if parsed.scheme in ('https', 'http') and parsed.netloc else '无可访问原文链接'
        details = ' · '.join(esc(s.get(k, '未知')) for k in ('publisher', 'published', 'accessed'))
        sources.append(f'<article id="{anchors[s["id"]]}"><h3>{esc(s["id"])} · {esc(s["title"])}</h3><p>{details}</p><p>源头：{esc(s.get("origin", "未知"))}</p><p>限制：{esc(s.get("limits", "未知"))}</p>{link}</article>')
    blocks.append(section('07 / 来源账本', sources))
    reader_html = ''
    if d.get('reader'):
        reader = d['reader']
        reader_html = section('三个问题，看懂这件事', [f'<article><h3>{esc(x["name"])}</h3><p>{esc(x["text"])}</p>{refs(x)}</article>' for x in reader['questions']])
        rows = ''.join(f'<tr><td>{esc(x["condition"])}</td><td>{esc(x["action"])}</td></tr>' for x in reader['routes'])
        reader_html += '<section><h2>接下来应该怎么处理</h2><p class="muted">以下是条件处理建议，不是已公布的调查结论。</p><table><thead><tr><th>核查结果</th><th>应有处理</th></tr></thead><tbody>' + rows + '</tbody></table><article><h3>消费者现在可以做什么</h3><p>' + esc(reader['next_step']) + '</p></article></section>'
        blocks = ['<details><summary>查看完整证据与分析</summary><p>' + esc(d['scope']) + '</p>' + ''.join(blocks) + '</details>']
    css = '''*{box-sizing:border-box}body{margin:0;background:#eef1f3;color:#182b38;font:17px/1.75 system-ui,-apple-system,"PingFang SC",sans-serif}main{max-width:1040px;margin:auto;padding:40px 24px}header{background:#102e3d;color:#fff;padding:36px;border-radius:20px}h1{font-size:clamp(27px,4vw,42px);line-height:1.35;margin:12px 0 24px}h2{font-size:23px;margin-top:36px}h3{font-size:18px;margin:8px 0}table{width:100%;border-collapse:collapse;background:white}th,td{padding:14px;text-align:left;border:1px solid #d8e1e6;vertical-align:top}summary{cursor:pointer;padding:20px;font-weight:600;background:#dce7eb;border-radius:12px}details{margin-top:28px}p{white-space:pre-wrap;overflow-wrap:anywhere}article{background:white;padding:22px;margin:14px 0;border-radius:14px;break-inside:avoid;overflow-wrap:anywhere}.badge{display:inline-block;border:1px solid #8c6511;background:#fff4d6;color:#6a4a00;border-radius:20px;padding:2px 12px;font-size:14px}.refs,.muted,footer{font-size:14px;color:#536b76}a{color:#075a91;overflow-wrap:anywhere}.timeline{border-left:5px solid #207d7a}.unknown{border-left:5px solid #c18723}blockquote{margin:0;padding:15px;border-left:4px solid #207d7a;background:#edf5f4}.columns{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.columns p{font-size:16px}.label{color:#8fdbcc;letter-spacing:2px;font-size:13px}@media(max-width:680px){main{padding:16px}header{padding:24px}.columns{grid-template-columns:1fr;gap:0}article{padding:18px}}@media print{body{background:white}main{padding:0;max-width:none}header{background:white;color:#182b38;border:2px solid #182b38}article{border:1px solid #ccc}a{color:inherit}.label{color:#182b38}}'''
    return f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(d["title"])}</title><style>{css}</style><main><header><div class="label">汽车新闻 · 证据与边界</div><h1>{esc(d["title"])}</h1><p>核查截至：{esc(d["as_of"])}</p>{("" if d.get("reader") else "<p>" + esc(d["scope"]) + "</p>")}<p>{esc(d["summary"])}</p></header>{reader_html}{"".join(blocks)}<footer><p>{esc(d["revision"])}</p><p>AI辅助整理。页面排版不代表真实性认证；结论以可追溯证据及适用范围为准。</p></footer></main></html>'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        document = render(json.loads(args.input.read_text(encoding='utf-8')))
    except (KeyError, ValueError, TypeError) as error:
        parser.error(str(error))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(document, encoding='utf-8')
    print(args.output.resolve())

if __name__ == '__main__':
    main()
