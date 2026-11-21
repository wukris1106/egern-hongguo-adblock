#!/usr/bin/env python3
"""校验 red-fruit Egern 模块：结构、正则、顺序遮蔽、真实域名判定"""
import yaml, re, sys, json

cfg = yaml.safe_load(open('/root/hongguo-egern/hongguo-adblock.yaml'))
rules = cfg['rules']
assert isinstance(rules, list) and rules, 'rules 为空'

def norm(r):
    k = list(r.keys())[0]
    return k, r[k]['match'], r[k]['policy']

parsed = [norm(r) for r in rules]

# 1. 正则合法性
errs = []
for k, m, p in parsed:
    if k not in ('domain','domain_suffix','domain_keyword','domain_regex'):
        errs.append('未知类型 %s' % k)
    if k == 'domain_regex':
        try:
            re.compile(m)
        except re.error as e:
            errs.append('正则错误 %s : %s' % (m, e))
    if p not in ('REJECT','DIRECT'):
        errs.append('未知策略 %s' % p)
print('结构问题:', errs or '无')

def hit(k, m, host):
    if k == 'domain':
        return host == m
    if k == 'domain_suffix':
        return host == m or host.endswith('.' + m)
    if k == 'domain_keyword':
        return m in host
    if k == 'domain_regex':
        return re.fullmatch(m, host) is not None
    return False

def decide(host):
    for k, m, p in parsed:
        if hit(k, m, host):
            return p, k, m
    return 'DEFAULT', '-', '-'

# 2. 顺序遮蔽：任何 DIRECT 规则命中的域名，必须先于它被 REJECT 捕获时不受影响；
#    这里反过来检查：REJECT 规则自己（用它的字面量当域名）是否被更早的 DIRECT 抢走
shadow = []
for i, (k, m, p) in enumerate(parsed):
    if p != 'REJECT' or k not in ('domain', 'domain_suffix'):
        continue
    for k2, m2, p2 in parsed[:i]:
        if p2 == 'DIRECT' and hit(k2, m2, m):
            shadow.append((m, '被更早的 DIRECT %s 抢走' % m2))
print('顺序遮蔽:', shadow or '无')

# 3. 真实域名判定（漫剧 dex 实证 + 短剧抓包）
cases = {
    # 必须 REJECT
    'ad.zijieapi.com': 'REJECT',
    'ads.zijieapi.com': 'REJECT',
    'ads5-normal-hl.zijieapi.com': 'REJECT',
    'ads3-normal.zijieapi.com': 'REJECT',
    'minigame5-normal-lq.zijieapi.com': 'REJECT',
    'api-access.pangolin-sdk-toutiao.com': 'REJECT',
    'gromore.pangolin-sdk-toutiao.com': 'REJECT',
    'log-api.pangolin-sdk-toutiao.com': 'REJECT',
    'pangolin5.snssdk.com': 'REJECT',
    'lf3-mgsdk-sign.dailygn.com': 'REJECT',
    'lf6-developer-sign.bytemastatic.com': 'REJECT',
    'p3-ad-sign.byteimg.com': 'REJECT',
    'p9-ad-sign.byteimg.com': 'REJECT',
    'p1-luckycatopen.byteimg.com': 'REJECT',
    'v5-reading-ad.qznovelvod.com': 'REJECT',
    'v11-reading-ad.qznovelvod.com': 'REJECT',
    'v5-bd-daily-reading-ad.qznovelvod.com': 'REJECT',
    'v5-se-sjy-daily-reading-ad.qznovelvod.com': 'REJECT',
    'isaas5-normal-hl.ecombdapi.com': 'REJECT',
    'ecom3-normal-hl.ecombdapi.com': 'REJECT',
    'mon11-misc-hl.fqnovel.com': 'REJECT',
    'log5-applog-lf.fqnovel.com': 'REJECT',
    'i.snssdk.com': 'REJECT',
    'mon.zijieapi.com': 'REJECT',
    'zlink.toutiao.com': 'REJECT',
    'www.chengzijianzhan.com': 'REJECT',
    'dig.bdurl.net': 'REJECT',
    'dig.zjurl.cn': 'REJECT',
    # 必须 DIRECT / 不被拦
    'v5-se2-alismart-reading-video.qznovelvod.com': 'DIRECT',
    'n98-v-readingvideo.qznovelvod.com': 'DIRECT',
    'v0-video-cn-private.qznovelvod.com': 'DIRECT',
    'lfdq-fq-tts.fqnovelvod.com': 'DIRECT',
    'reading.snssdk.com': 'DIRECT',
    'api5-normal-hl.fqnovel.com': 'DIRECT',
    'api3-normal-sinfonlineb.fqnovel.com': 'DIRECT',
    'security.snssdk.com': 'DIRECT',
    'is.snssdk.com': 'DIRECT',
    'verify.zijieapi.com': 'DIRECT',
    'polaris.zijieapi.com': 'DIRECT',
    'p3-reading.byteimg.com': 'DIRECT',
    'p1-reading.byteimg.com': 'DIRECT',
    'p9-reading.byteimg.com': 'DIRECT',
    'p3-novel.byteimg.com': 'DIRECT',
    'p6-novel.byteimg.com': 'DIRECT',
    'p26-tt.byteimg.com': 'DIRECT',
    'lf3-reading.fqnovelpic.com': 'DIRECT',
    'lf26-reading.fqnovelstatic.com': 'DIRECT',
    'ttcdn-tos.pstatp.com': 'DIRECT',
    'p3-piu.byteimg.com': 'DIRECT',
    'lf3-developer.bytemastatic.com': 'DIRECT',
    'hongguo.douyin.com': 'DIRECT',
}
bad = []
for host, want in cases.items():
    got, k, m = decide(host)
    ok = (got == want) or (want == 'DIRECT' and got in ('DIRECT', 'DEFAULT'))
    if not ok:
        bad.append((host, want, got, k, m))
print('判定用例: %d 条, 失败 %d' % (len(cases), len(bad)))
for b in bad:
    print('   ✗', b)

# 4. 全量跑一遍真实域名（漫剧 dex 提取的 2002 条里筛真域名）
doms = json.load(open('/root/hongguo-egern/kylin-domains.json'))
real = [d for d in doms if not d.startswith(('com.','cn.','net.','org.','android.','androidx.','java.','kotlin.','libcore','javax','kotlinx','xmlpull','coil3'))]
rej = sorted(h for h in real if decide(h)[0] == 'REJECT')
print('\n漫剧 dex 域名里被判 REJECT 的：')
for h in rej:
    print('   ', h, '←', decide(h)[1])
print('\n总结：规则 %d 条（REJECT %d / DIRECT %d）' % (
    len(parsed), sum(1 for x in parsed if x[2]=='REJECT'), sum(1 for x in parsed if x[2]=='DIRECT')))
sys.exit(1 if (errs or shadow or bad) else 0)
