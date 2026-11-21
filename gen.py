#!/usr/bin/env python3
# 生成红果短剧/漫剧 Egern 去广告模块 YAML（单引号标量，正则不转义）
import yaml

SECS = []
def sec(title, note=None):
    SECS.append(('comment', title, note))
def rule(kind, match, policy='REJECT'):
    SECS.append(('rule', kind, match, policy))

# ── 0
sec("0. 断 HTTPDNS 旁路 — 红果系用自带 HTTPDNS 解析后裸 IP 直连，域名规则看不见流量",
    "dig.bdurl.net = TTNet native 硬编码 DNS（Android 包 mc5/a.java 实证）；dig.zjurl.cn = 备用 httpdns。断掉后 App 回退系统 DNS，下面的规则才生效")
rule('domain', 'dig.bdurl.net')
rule('domain', 'dig.zjurl.cn')

# ── 1
sec("1. 红果漫剧自有广告 API — com.kylin.read 7.4.5.32 反编译实证（24 处硬编码）",
    "ad.zijieapi.com/api/ad/v1/banner/ 与 /api/incentive/marketing/done：漫剧开屏 + 信息流 banner + 激励回传都走这个域，是漫剧第一大头")
rule('domain', 'ad.zijieapi.com')
rule('domain', 'ads.zijieapi.com')
rule('domain_regex', r'^ads[0-9]+-normal(?:-[a-z0-9]+)?\.zijieapi\.com$')
rule('domain_regex', r'^minigame[0-9]+-normal(?:-[a-z0-9]+)?\.zijieapi\.com$')
rule('domain', 'ad.toutiao.com')
rule('domain', 'leads.oceanengine.com')

# ── 2
sec("2. 穿山甲 / CSJ 广告 SDK（两个 App 都内置 com.bytedance.sdk.openadsdk）")
rule('domain_suffix', 'pangolin-sdk-toutiao.com')
rule('domain_suffix', 'pangolin-sdk-toutiao1.com')
rule('domain_suffix', 'pangolin-sdk-toutiao-b.com')
rule('domain_suffix', 'pglstatp-toutiao.com')
rule('domain_suffix', 'pglstatp-toutiao-b.com')
rule('domain_suffix', 'pangle.io')
rule('domain', 'ad.pangle.cn')
rule('domain', 'ad.pangolin.cn')
rule('domain_regex', r'^pangolin[^.]*\.snssdk\.com$')
rule('domain', 'csjdeveloper.com')
rule('domain', 'scsjsd.com')

# ── 3
sec("3. 广告素材签名 CDN / 广告安装包",
    "漫剧 dex 实证：lf3/lf6/lf9-mgsdk-sign.dailygn.com、lf*-developer-sign.bytemastatic.com、p1-luckycatopen.byteimg.com；只拦带 -sign 的广告子域，byteimg/bytemastatic 主体在第 9 段白名单放行")
rule('domain_keyword', '-ad-sign.byteimg.com')
rule('domain_keyword', '-mgsdk-sign')
rule('domain_keyword', '-developer-sign.bytemaimg.com')
rule('domain_keyword', '-developer-sign.bytemastatic.com')
rule('domain_keyword', '-open-ma-pkg-sign.bytemastatic.com')
rule('domain', 'p1-luckycatopen.byteimg.com')

# ── 4
sec("4. 贴片 / 插播广告视频 CDN（v5/v11/v26-reading-ad 等）",
    "正片走 *-reading-video.qznovelvod.com，由第 9 段的 qznovelvod.com DIRECT 保住")
rule('domain_regex', r'^v[0-9]+-(?:[a-z]+-)*reading-ad\.qznovelvod\.com$')

# ── 5
sec("5. 广告跳转短链 / 落地页")
rule('domain', 'zlink.ugsdk.cn')
rule('domain_suffix', 'praisewindow.ugsdk.cn')
rule('domain_keyword', 'chengzijianzhan')
rule('domain', 'activity-ag.awemeughun.com')
rule('domain', 'zlink.toutiao.com')
rule('domain', 'zlink.fqnovel.com')

# ── 6
sec("6. 伪装随机子域广告 CDN（Android 真机 DNS 实抓确认，纯广告域名）")
for d in ['comfylink.com', 'ndcpp.com', 'ydycdn.com', 'qrstuvwxyzab.com',
          'wuchuyun.com', 'xinqiucc.com', 'jomoxc.com', 'wmzfylgdsz.com']:
    rule('domain_suffix', d)

# ── 7
sec("7. 电商推广位（红果内置商城 / 商品卡）— 想用商城就把这 4 条删掉或注释",
    "红果内带货卡片、商品卡、商城推荐位都调这三个 ecombdapi 子域族")
rule('domain_regex', r'^ecom[^.]*-normal[^.]*\.ecombdapi\.com$')
rule('domain_regex', r'^ec[^.]*-core[^.]*\.ecombdapi\.com$')
rule('domain_regex', r'^isaas[^.]*-normal[^.]*\.ecombdapi\.com$')
rule('domain_suffix', 'ecombdpage.com')

# ── 8
sec("8. 埋点 / 上报（不影响播放；若出现登录异常，先把 i*/log* 这十几条注释掉）",
    "security.snssdk.com、is.snssdk.com、verify.zijieapi.com 是风控与登录，故意不动")
for h in ['i.snssdk.com', 'i-lq.snssdk.com', 'i-hl.snssdk.com', 'ib-lq.snssdk.com',
          'mon.zijieapi.com', 'applog.zijieapi.com', 'log.zijieapi.com',
          'rtlog.zijieapi.com', 'timon.zijieapi.com',
          'mon.snssdk.com', 'applog.snssdk.com', 'log.snssdk.com',
          'rtlog.snssdk.com', 'report.snssdk.com',
          'mon.toutiaocloud.net', 'mon.toutiaocloud.com', 'mon.toutiao.com',
          'monsetting.toutiao.com', 'ichannel.snssdk.com']:
    rule('domain', h)
rule('domain_keyword', 'applog.fqnovel.com')
rule('domain_regex', r'^(?:mon|r?t?log)[0-9]*(?:-[a-z0-9]+)*\.fqnovel\.com$')

# ── 9
sec("9. 内容 / 正片 / 图床白名单 — 全 DIRECT，防误伤（顺序必须在所有 REJECT 之后）",
    "漫剧实证内容域：reading.snssdk.com、api3/api5-normal[-hl/-lf/-lq].fqnovel.com、p1/p3/p9-reading.byteimg.com、p3/p6-novel.byteimg.com、lf3/lf26-reading.fqnovelpic|static.com、v0-video-cn-private.qznovelvod.com")
for d in ['qznovelvod.com', 'fqnovelvod.com', 'fqnovel.com', 'fqnovelpic.com', 'fqnovelstatic.com',
          'byteimg.com', 'bytemaimg.com', 'bytemastatic.com', 'dailygn.com', 'pstatp.com',
          'snssdk.com', 'zijieapi.com', 'bytedanceapi.com', 'toutiao.com',
          'toutiaocloud.net', 'toutiaocloud.com',
          'hongguo.com', 'douyin.com', 'douyinpic.com', 'douyinstatic.com', 'ecombdimg.com',
          'bytegecko.com', 'bytefae.com', 'bytednsdoc.com', 'draftstatic.com', 'toutiaostatic.com',
          'ixigua.com', 'bytecdn.cn', 'zjcdn.com']:
    rule('domain_suffix', d, 'DIRECT')

# ── 可选段（默认注释）
OPTIONAL = [
    ("附 A. 红果内直播带货卡片（信令层）— 刷剧时右侧飘商品卡 / 「XX 正在直播」才打开",
     ['webcast*-open*.douyin.com', 'content-open.douyin.com'],
     "打开后红果内直播带货卡与伪装直播卡会消失；代价是本机抖音系 App 的直播间页面也会受影响，自己权衡"),
    ("附 B. 全量 HTTPDNS 关键字封杀 — 上面 dig.* 还不够时再开",
     ['httpdns'],
     "会把所有 App 的 HTTPDNS 都断掉（抖音、番茄等全受影响），只在 dig.* 无效时启用"),
    ("附 C. 白山云字节节点（广告素材嫌疑，多源未定论）",
     ['v9-default.tt.x.bsgslb.cn'],
     "拦了只影响广告素材加载；正片出现异常先删这条"),
]

HEADER = '''name: "红果短剧 / 红果漫剧 去广告"
description: "域名层拦截穿山甲 SDK、红果漫剧自有广告 API(ad.zijieapi.com)、广告素材签名 CDN、贴片广告 CDN、广告落地页与埋点上报；正片/封面/登录/支付全部放行。纯规则，不需要 MITM 证书。"
author: "思思（wukris1106）"
homepage: "https://github.com/wukris1106/egern-hongguo-adblock"
icon: "nosign"

# ═══════════════════════════════════════════════════════════
#  红果短剧（com.phoenix.read · iOS「红果免费短剧」）
#  红果漫剧（com.kylin.read）
#  ---------------------------------------------------------
#  · 规则自上而下 = 优先级：所有 REJECT 在前，白名单 DIRECT 在后
#  · 漫剧域名：com.kylin.read 7.4.5.32 官方包 25 个 dex 反编译实证
#  · 短剧域名：iOS 实机抓包 + 多个已实机验证的社区模块交叉
#  · 为什么不用 MITM：番茄系 TTNet/Cronet 只信系统信任库，用户 CA 必被拒；
#    且 ad.zijieapi.com / ecombdapi / *-ad-sign 有证书固定 → 规则层最稳
#  · 装完杀掉 App 重开，本地缓存的开屏素材要等过期才消失
# ═══════════════════════════════════════════════════════════

rules:
'''

def q(s):
    return "'" + s.replace("'", "''") + "'"

lines = [HEADER]
for item in SECS:
    if item[0] == 'comment':
        _, title, note = item
        lines.append('  # ── %s\n' % title)
        if note:
            lines.append('  #    %s\n' % note)
    else:
        _, kind, match, policy = item
        lines.append('  - %s:\n      match: %s\n      policy: %s\n' % (kind, q(match), policy))

lines.append('\n  # ═══════════════════════════════════════════════════════\n'
             '  #  可选段（默认全部注释，需要时把对应行前面的 # 去掉）\n'
             '  # ═══════════════════════════════════════════════════════\n')
for title, hosts, note in OPTIONAL:
    lines.append('  # %s\n  #   %s\n' % (title, note))
    for h in hosts:
        if '*' in h:
            kind, m = 'domain_regex', '^' + h.replace('*', '[a-z0-9-]*').replace('.', r'\.') + '$'
        elif h == 'httpdns':
            kind, m = 'domain_keyword', 'httpdns'
        else:
            kind, m = 'domain', h
        lines.append('  # - %s:\n  #     match: %s\n  #     policy: REJECT\n' % (kind, q(m)))

body = ''.join(lines)
open('/root/hongguo-egern/hongguo-adblock.yaml', 'w').write(body)

cfg = yaml.safe_load(body)
rules = cfg['rules']
parsed = [(list(r)[0], r[list(r)[0]]['match'], r[list(r)[0]]['policy']) for r in rules]
print('total rules:', len(parsed))
print('REJECT:', sum(1 for x in parsed if x[2] == 'REJECT'), '| DIRECT:', sum(1 for x in parsed if x[2] == 'DIRECT'))
print('types:', {k: sum(1 for x in parsed if x[0] == k) for k in ['domain', 'domain_suffix', 'domain_keyword', 'domain_regex']})
print('sample:', parsed[:2], parsed[-2:])
print('bytes:', len(body))
