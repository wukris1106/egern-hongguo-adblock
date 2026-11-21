# 红果短剧 / 红果漫剧 去广告 · Egern 模块

纯**域名规则层**模块，一个模块同时管两个 App：

- 红果短剧（Android `com.phoenix.read` · iOS「红果免费短剧」）
- 红果漫剧（`com.kylin.read`）

不需要 MITM、不需要装证书、没有远程脚本 —— 不会出现「脚本拉不到所以静默不生效」那类问题。

## 导入

模块（Egern → 工具 → 模块 → 新建 → 从 URL 导入）：

```
https://cdn.jsdelivr.net/gh/wukris1106/egern-hongguo-adblock@main/hongguo-adblock.yaml
```

备用直链（jsDelivr 挂了再用）：

```
https://raw.githubusercontent.com/wukris1106/egern-hongguo-adblock/main/hongguo-adblock.yaml
```

装完：杀掉红果进程重开 → 先看开屏广告有没有过。

## 拦什么（94 条规则：65 REJECT / 29 DIRECT）

| 段 | 目标 | 依据 |
|---|---|---|
| 0 | 断 HTTPDNS 旁路（`dig.bdurl.net` / `dig.zjurl.cn`） | 番茄系 App 用自带 HTTPDNS 解析后裸 IP 直连，域名规则会漏；断掉逼它回系统 DNS |
| 1 | **漫剧自有广告 API**：`ad.zijieapi.com`（`/api/ad/v1/banner/`、`/api/incentive/marketing/done`）、`ads.zijieapi.com`、`ads3/5-normal[-hl/-lf/-lq]`、`minigame*-normal` | 漫剧 APK 25 个 dex 反编译，24 处硬编码 |
| 2 | 穿山甲 / CSJ SDK 全家（pangolin / pglstatp / pangle） | 两个 App 都内置 `com.bytedance.sdk.openadsdk` |
| 3 | 广告素材签名 CDN：`*-ad-sign.byteimg.com`、`*-mgsdk-sign.dailygn.com`、`*-developer-sign.bytemastatic.com`、`*-open-ma-pkg-sign.*`、`p1-luckycatopen` | 漫剧 dex 实证（lf3/lf6/lf9 机房前缀） |
| 4 | 贴片/插播广告视频 `v{N}-*-reading-ad.qznovelvod.com` | 正片是 `*-reading-video`，同域不同前缀 |
| 5 | 广告短链与落地页：`zlink.ugsdk.cn`、`zlink.toutiao.com`、`zlink.fqnovel.com`、`chengzijianzhan*`、`praisewindow` | 多源实机抓包一致 |
| 6 | 伪装随机子域广告 CDN（`ndcpp.com`、`ydycdn.com`、`jomoxc.com` 等 8 个） | Android 真机 DNS 实抓 |
| 7 | 电商推广位：`{ecom,ec,isaas}*-normal*.ecombdapi.com`、`ecombdpage.com` | 红果内商品卡 / 商城推荐位 |
| 8 | 埋点上报：`i.snssdk.com`、`mon/log/rtlog/timon.*`、`mon{N}-misc*.fqnovel.com` | 减掉无效流量，不影响播放 |
| 9 | **白名单 DIRECT**：qznovelvod / fqnovel* / byteimg / pstatp / snssdk / zijieapi / bytemastatic / dailygn 等 29 条 | 正片、封面、漫画图、登录、支付全在这里，顺序在所有 REJECT 之后 |

## 明确不拦（拦了会出事）

- `qznovelvod.com` 正片、`*-reading-video*`、`fqnovelvod.com`（TTS）
- `p*-reading.byteimg.com` / `p*-novel.byteimg.com` / `fqnovelpic` / `fqnovelstatic`（封面与漫画图）
- `security.snssdk.com`、`is.snssdk.com`、`verify.zijieapi.com`（风控与登录）
- `api3/api5-normal*.fqnovel.com`、`reading.snssdk.com`（内容 API）
- `bytegecko.com`（H5 离线包）、`pitaya`、`douyinpic`/`ecombdimg`（通用图床）

## 已知边界

1. **本地已缓存的广告**（开屏素材包）不会立刻消失，等过期或重装 App。规则只挡新请求。
2. **不走 MITM**。番茄系 TTNet/Cronet 只信系统信任库，用户 CA 必被拒；`ad.zijieapi.com`、`ecombdapi`、`*-ad-sign` 还有证书固定。所以 `gurd.snssdk.com/src/server/v1/package`（开屏包路径）这类**路径级**拦截做不了，只能靠域名层。
3. **直播插播 / 拉流广告**（`pull-flv-*.douyincdn.com` 明文 HTTP + 裸 IP）在 Egern 域名层拦不到，且拦 `douyincdn` 会连带本机所有抖音系直播。需要的话单独用 URL Rewrite 处理，别往这个模块里塞。
4. 广告被 REJECT 后 SDK 会重试几次，属正常，几秒后自己放弃。
5. 金币激励任务会一并失效（金币功能官方已公告 2026-12-31 前下线）。

## 出问题怎么回退（模块内注释即关）

| 症状 | 关掉哪段 |
|---|---|
| 红果打不开 / 一直转圈 | 先删第 0 段 `dig.*` 两条 |
| 登录异常 / 验证码刷不出 | 删第 8 段 `i*.snssdk.com` 那几条 |
| 商城 / 商品卡要用 | 删第 7 段 4 条 |
| 正片黑屏 / 封面白图 | 检查用户自己的 profile 里有没有更靠前的 `DOMAIN-SUFFIX` 规则抢走（模块规则只有排在它前面才生效） |

## 附：可选段（默认注释在文件末尾）

- 附 A：红果内直播带货卡片信令（`webcast*-open*.douyin.com`）—— 打开后卡片消失，但本机抖音系 App 直播间页面会受影响。
- 附 B：全量 `httpdns` 关键字封杀 —— 所有 App 的 HTTPDNS 都断，只在附 0 无效时用。
- 附 C：`v9-default.tt.x.bsgslb.cn` 白山云节点 —— 素材嫌疑，未定论。

## 规则维护

```bash
python3 gen.py          # 重新生成 hongguo-adblock.yaml
python3 verify_module.py # 结构 / 正则 / 顺序遮蔽 / 51 条真实域名判定
```

`verify_module.py` 会跑三类检查：正则合法性、有没有被更早的 DIRECT 抢走、以及拿漫剧 APK 里真实提取的域名逐个判定。

## 致谢

短剧侧域名与实测结论交叉自：`qq2519157/adblock-modules`（iPad 实测 + Android 反编译）、`k6nfmm7dbr-commits/hongguo-lite`、`laincat/Rules`、`abclq/home-dns-adblock`（558 域 DNS 实抓）、`lzwsoldier/stash-hongguo-adblock`。
漫剧侧域名由本仓库自行反编译 `com.kylin.read` 7.4.5.32 得到。
