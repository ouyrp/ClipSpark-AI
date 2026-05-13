# ClipSpark AI 素材库接入候选

## 接入原则

素材库不要只按“免费”判断，要按授权类型分层：

- 开源/开放许可：适合做默认素材库。
- CC0：适合直接内置或缓存。
- CC BY：可用，但需要保留作者和来源。
- 免费商业授权：可用，但通常不能作为独立素材二次分发。
- 非商业授权：默认不进生产素材库。

## 推荐优先级

### 1. 音效和转场声音

#### Freesound

- 类型：音效、环境声、转场声、拟音。
- 授权：Creative Commons，包含 CC0、CC BY、CC BY-NC。
- 接入：有 API，可检索声音、标签、相似声音和音频分析数据。
- 建议：只自动使用 CC0 和 CC BY，过滤 CC BY-NC。
- 官网：https://freesound.org
- API：https://freesound.org/docs/api

#### SoundSpool

- 类型：聚合 Freesound 的免费音效。
- 授权：CC 许可，页面展示 CC0/CC BY 等。
- 建议：适合作为发现和人工筛选来源。
- 官网：https://soundspool.com

#### Directory.Audio

- 类型：音效、音乐、intro。
- 授权：Creative Commons，包含 CC0、署名、非商业等。
- 建议：先接 CC0/署名类，不接非商业类。
- 官网：https://directory.audio

#### lotsofsounds

- 类型：音效。
- 授权：页面说明全站 CC0。
- 接入：提供 REST API。
- 建议：适合做第一批内置音效池，例如 whoosh、hit、transition、sparkle。
- 官网：https://www.lotsofsounds.com/sounds

### 2. BGM

#### Mixkit

- 类型：音乐、音效、视频、模板。
- 授权：Mixkit Free License，免费商用，通常不要求署名。
- 注意：不是开源素材，不能当作独立素材再分发售卖。
- 建议：适合作为用户生成视频里的 BGM 来源，不建议把原始素材打包出售。
- 官网：https://mixkit.co
- License：https://mixkit.co/license

#### Free To Use

- 类型：音乐。
- 接入：有公开 API，无需 API key。
- 注意：免费使用有条件，商业使用可能需要付费许可证。
- 建议：可以作为“试用音乐源”，生产前需要做许可证确认。
- API：https://freetouse.com/api

### 3. 动效、贴纸和覆盖层

#### LottieFiles Free Animations

- 类型：Lottie 动画、GIF、MP4 动效。
- 授权：Lottie Simple License，免费动画可商用、可修改。
- 注意：不能批量抓取并做竞争性素材服务，不能把原始动画文件作为独立素材转售。
- 建议：接入方式为用户选择/下载后渲染进视频，不做大规模镜像。
- 官网：https://lottiefiles.com
- License 说明：https://help.lottiefiles.com/animation-licensing-basics-

#### 自建 FFmpeg 动效库

- 类型：烟花、闪白、胶片颗粒、速度线、光晕、边框、标题条、转场。
- 授权：自研，无版权风险。
- 建议：作为默认基础特效库，当前项目已开始用 FFmpeg 滤镜实现。

### 4. 视频 B-roll 和背景素材

#### Pexels

- 类型：照片、视频。
- 授权：Pexels License，免费商用，不要求署名。
- 接入：有 API。
- 注意：不能把素材作为独立素材出售/分发，不要暗示人物/品牌背书。
- 建议：适合为视频补 B-roll，但要记录来源和 license。
- API：https://www.pexels.com/api/documentation/
- License：https://www.pexels.com/license/

#### Openverse

- 类型：开放许可图片和音频。
- 授权：Creative Commons 或公有领域。
- 接入：有 API。
- 注意：Openverse 提醒应验证单个作品许可证准确性。
- 建议：适合做开放素材搜索入口，入库前保存 license_url。
- API：https://docs.openverse.org/api/

#### Mixkit / Videvo

- 类型：视频、motion graphics、模板、音效、音乐。
- 授权：各素材类型不同，免费和付费混合。
- 建议：只作为可选外部来源，必须保存每个素材的许可证字段。

### 5. 视频编辑引擎和转场库

#### libopenshot

- 类型：开源视频编辑库。
- 授权：LGPL v3 或商业授权。
- 能力：视频格式、剪辑、转场、效果。
- 建议：如果后续 FFmpeg 手写滤镜维护成本高，可以评估接入。
- 官网：https://www.openshot.org/libopenshot/

#### Vanta

- 类型：基于 Remotion 的开源 AI 视频引擎。
- 能力：时间线、转场、字幕、motion graphics 等。
- 建议：适合研究 Remotion 资产组织方式和转场实现，但需单独审 license 和成熟度。
- GitHub：https://github.com/itsjwill/vanta

## 第一阶段建议接入

1. 自建 FFmpeg 特效库：无版权风险，先覆盖基础视觉效果。
2. lotsofsounds：接 CC0 音效，补充 whoosh、hit、transition、sparkle。
3. Freesound：接 CC0/CC BY 音效，保留作者和来源。
4. LottieFiles：用于 sticker/粒子/动态图层，但不做批量镜像。
5. Pexels：用于 B-roll 搜索和补画面，不作为原始素材分发。

## 入库字段建议

```json
{
  "id": "asset_001",
  "provider": "freesound",
  "type": "sound_effect",
  "category": "transition",
  "tags": ["whoosh", "hit"],
  "license": "CC0",
  "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
  "creator": "creator_name",
  "source_url": "https://example.com/item",
  "download_url": "https://example.com/file.mp3",
  "local_url": "/media/library/item.mp3",
  "attribution_required": false,
  "commercial_allowed": true
}
```

## 风险控制

- 默认只自动使用 CC0、Pexels License、Mixkit Free License 和明确可商用素材。
- CC BY 素材必须在成片元数据或导出说明里保留 attribution。
- 不接 CC BY-NC 到商业出片路径。
- 不把 Pexels、Mixkit、LottieFiles 原始素材作为独立素材包二次分发。
- 所有第三方素材都保存 source_url、license、creator，方便追溯。
