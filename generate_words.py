"""
Batch word entry generator for EnStory Jekyll site.
Generates _words/*.md files with etymology, timeline, roots, related words.
"""
import json
import os
import re

# ─────────────────────────────────────────────────────────────────────────────
# Rich etymology/phonetic/tags database for known words
# Format: word -> {phonetic, etymology, timeline, roots, related, tags, body, pos_override}
# ─────────────────────────────────────────────────────────────────────────────
WORD_DB = {
    "crane": {
        "phonetic": "/kreɪn/",
        "etymology": "来自古英语 **cran**，源自原始日耳曼语 *kranaz*，与荷兰语 *kraan*、德语 *Kran* 同根。最初专指鹤这种长颈候鸟，因起重机的形状与鹤伸颈的姿态酷似，故将鸟名转用于机械。",
        "timeline": [
            ("古英语（约 900）", "cran 指代鹤鸟，源于鸟鸣声的拟声。"),
            ("中世纪（约 13 世纪）", "词义扩展至起重机械，因其长臂结构形似鹤颈。"),
            ("现代英语", "crane 兼指鸟类与机械，并有动词用法「伸长脖子张望」。"),
        ],
        "roots": [("cran", "古英语/日耳曼语", "鹤，因形似而借指机械")],
        "related": ["heron", "derrick", "winch"],
        "tags": ["古英语源", "名词", "自然与机械"],
        "body": "**Crane** 是英语中少见的「鸟→机械」词义迁移范例。当你仰望建筑工地上高耸的起重臂时，不妨想象一只鹤优雅地伸颈俯视——那正是这个词的原始画面。\n\n动词用法「crane one's neck」（伸长脖子）也保留了最初的鸟类意象，让词语的生命得以延续。",
    },
    "materialism": {
        "phonetic": "/məˈtɪər.i.ə.lɪ.z(ə)m/",
        "etymology": "由 **material**（物质的，源自拉丁语 *materia* = 木料、物质）+ **-ism**（主义、学说）构成。17 世纪哲学术语，指一切现象皆由物质决定的世界观。",
        "timeline": [
            ("拉丁语", "materia 意为「木料、原材料」，引申为「物质」。"),
            ("17 世纪", "英语 materialism 作为哲学术语出现，对立于 idealism（唯心主义）。"),
            ("19—20 世纪", "马克思主义将辩证唯物主义（dialectical materialism）推向全球。"),
            ("现代", "日常语境中常指对物质财富的过度追求，带有负面含义。"),
        ],
        "roots": [
            ("materia", "拉丁语", "木料、物质"),
            ("-al", "拉丁语后缀", "形容词化"),
            ("-ism", "希腊语后缀", "主义、学说"),
        ],
        "related": ["idealism", "empiricism", "pragmatism", "capitalism"],
        "tags": ["拉丁语源", "哲学", "名词"],
        "body": "**Materialism** 在哲学与日常语言中呈现出截然不同的面貌：哲学家眼中的唯物主义是一套严密的本体论，而普通人口中的 materialism 往往意味着对名牌与财富的执念。\n\n这个词提醒我们，同一个词根如何在不同语境中生长出完全不同的含义。",
    },
    "veto": {
        "phonetic": "/ˈviː.toʊ/",
        "etymology": "直接借自拉丁语 **veto**，意为「我禁止」（第一人称单数现在时），是动词 *vetare*（禁止）的变形。罗马时代护民官（tribunes）以此词阻止元老院决议，是共和政制的重要工具。",
        "timeline": [
            ("古罗马", "护民官高呼 'Veto!'（我禁止！）以阻止对平民不利的法令，成为宪政经典。"),
            ("17 世纪", "英语吸收此词，用于描述君主或行政长官的否决权。"),
            ("1945 年", "《联合国宪章》赋予五常一票否决权（veto power），veto 成为国际政治核心词汇。"),
        ],
        "roots": [("veto", "拉丁语", "我禁止，来自动词 vetare")],
        "related": ["prohibit", "overrule", "sanction", "veto power"],
        "tags": ["拉丁语源", "法律政治", "动词"],
        "body": "**Veto** 是为数不多直接以第一人称动词形式进入英语的拉丁词——「我禁止」本身就是词语的本体。两千年前罗马护民官的一声呼喝，演变成了今天联合国安理会上最有分量的一个词。",
    },
    "dreadful": {
        "phonetic": "/ˈdred.fəl/",
        "etymology": "由 **dread**（极度恐惧，来自古英语 *drǣdan*）+ **-ful**（充满……的）构成。古英语 drǣdan 与古萨克逊语 *drādan* 同源，意指持续的深切恐惧。",
        "timeline": [
            ("古英语", "drǣdan 表示「持续地害怕」，尤指对神明或权力的敬畏恐惧。"),
            ("中世纪英语", "dread 作为名词确立，dreadful 形容词化出现于 14 世纪。"),
            ("现代", "词义有所弱化，日常口语中常指「很糟糕」，如 dreadful weather。"),
        ],
        "roots": [
            ("drǣdan", "古英语", "持续地恐惧"),
            ("-ful", "古英语后缀", "充满……的"),
        ],
        "related": ["terrible", "awful", "horrific", "appalling"],
        "tags": ["古英语源", "形容词", "情感"],
        "body": "**Dreadful** 起源于人类最原始的情感——对未知与强大力量的恐惧。今天它的语气已大为缓和，但那种充满阴暗感的词音（dr-），仍与 dreary、dark、dire 等词共同构成英语的「恐惧音群」。",
    },
    "brutal": {
        "phonetic": "/ˈbruː.t̬əl/",
        "etymology": "来自中世纪拉丁语 **brutalis**，由 *brutus*（迟钝的、动物性的）+ *-alis*（形容词后缀）构成。拉丁语 brutus 意为「沉重的、愚钝的、如同野兽的」，与动物 brute 同源。",
        "timeline": [
            ("拉丁语", "brutus 意为「重、钝、无理性」，常用于区分人类理性与动物本能。"),
            ("15 世纪", "英语 brutal 出现，形容残忍、缺乏理性的行为。"),
            ("现代", "词义延伸至「极度严酷」，如 brutal winter（严酷的冬天）、brutal honesty（赤裸的坦诚）。"),
        ],
        "roots": [
            ("brutus", "拉丁语", "沉重的、如野兽般的"),
            ("-al", "拉丁语后缀", "与……有关的"),
        ],
        "related": ["savage", "vicious", "cruel", "brute", "brutality"],
        "tags": ["拉丁语源", "形容词", "品性"],
        "body": "**Brutal** 的词根 *brutus* 在拉丁语中同时意指「沉重」与「野兽性」，暗示着一种没有理性光照的黑暗状态。凯撒被刺时的那句「Et tu, Brute?」中的 Brutus，其名字正含有这个词根的影子。",
    },
    "quench": {
        "phonetic": "/kwentʃ/",
        "etymology": "来自古英语 **cwencan**，意为「熄灭、扑灭」，词源与原始日耳曼语 *kwankwjan* 相关，有「使消失」之义。最初专指熄灭火焰，后引申至止渴、抑制欲望等。",
        "timeline": [
            ("古英语", "cwencan 意为「熄灭（火）」，用于炉火、燃烧等场景。"),
            ("中世纪", "词义扩展至「止渴」和「平息（感情、欲望）」。"),
            ("现代", "主要用法为 quench one's thirst（止渴）和 quench a flame（扑灭火焰）。"),
        ],
        "roots": [("cwencan", "古英语", "熄灭、使消失")],
        "related": ["extinguish", "satisfy", "slake", "suppress"],
        "tags": ["古英语源", "动词", "感官"],
        "body": "**Quench** 是一个充满动感的词——它描述了那种「彻底消除」的动作，无论是一捧冷水扑灭炭火，还是一杯凉茶化解燥渴。在冶金学中，quenching（淬火）则是用急速冷却来强化金属，词语在此获得了全新的专业生命。",
    },
    "prevalent": {
        "phonetic": "/ˈprev.ə.lənt/",
        "etymology": "来自拉丁语 **praevalens**（现在分词），由 *prae-*（在……之前）+ *valere*（有力量、有价值）构成，原意「力量超越众人的」，演变为「广泛存在的、占主导地位的」。",
        "timeline": [
            ("拉丁语", "praevaleō 意为「占优势、胜过」，用于法律和军事语境。"),
            ("17 世纪", "英语 prevalent 出现，指某事物在特定区域或时期内广泛流行。"),
            ("现代", "常用于描述疾病、观念、习俗的普遍性，如 prevalent disease（流行病）。"),
        ],
        "roots": [
            ("prae-", "拉丁语前缀", "在前、超越"),
            ("valere", "拉丁语", "强壮、有力量"),
        ],
        "related": ["widespread", "common", "pervasive", "dominant", "rampant"],
        "tags": ["拉丁语源", "形容词", "程度"],
        "body": "**Prevalent** 内含「力量」意象——一个观念或现象之所以流行，是因为它在竞争中获得了优势。这与 *prevail*（占上风）共享同一词根，提醒我们：流行从来不只是偶然，而是某种力量胜出的结果。",
    },
    "vanity": {
        "phonetic": "/ˈvæn.ɪ.ti/",
        "etymology": "来自古法语 **vanité**，源自拉丁语 **vanitas**（空虚、徒劳），由 *vanus*（空的、无实质的）+ *-itas*（名词后缀）构成。《圣经·传道书》中「虚空的虚空，凡事都是虚空」即用此词。",
        "timeline": [
            ("拉丁语", "vanus 意为「空的、无用的」，vanitas 指一切事物的短暂与虚无。"),
            ("中世纪", "基督教文学中 vanity 指对世俗荣耀的空洞追求。"),
            ("17 世纪", "《天路历程》中的 Vanity Fair（虚荣市集）使此词深入人心。"),
            ("现代", "除「自负」外，vanity 也指梳妆台（vanity table）和虚荣出版（vanity press）。"),
        ],
        "roots": [
            ("vanus", "拉丁语", "空的、无实质的"),
            ("-itas", "拉丁语后缀", "性质、状态"),
        ],
        "related": ["pride", "conceit", "arrogance", "hubris", "narcissism"],
        "tags": ["拉丁语源", "名词", "品性"],
        "body": "**Vanity** 在《圣经》的传道书中承载着整个人类文明的虚无感；在 Thackeray 的小说《名利场》（Vanity Fair）里，它变成了社会讽刺的利器；而在今天的梳妆间里，它平静地描述着一面镜子。从哲学到世俗，这个词走过了漫长的旅程。",
    },
    "brittle": {
        "phonetic": "/ˈbrɪt.əl/",
        "etymology": "来自古英语 *brytel*（易碎的），与 *brēotan*（打碎）相关，源自原始日耳曼语词根，意指「容易断裂的东西」。其词根与 *break*（打破）可能有远亲关系。",
        "timeline": [
            ("古英语", "与 brēotan（打碎、折断）同属日耳曼语系，描述易于碎裂的物质特性。"),
            ("中世纪", "brittle 在英语中稳定下来，描述玻璃、骨骼等硬而脆的物体。"),
            ("现代", "词义延伸至情感和关系：a brittle relationship（脆弱的关系）、brittle laughter（生硬的笑声）。"),
        ],
        "roots": [("brytel / brēotan", "古英语", "打碎、易裂")],
        "related": ["fragile", "frail", "delicate", "crispy"],
        "tags": ["古英语源", "形容词", "材料性质"],
        "body": "**Brittle** 描述的是一种特殊的脆弱：不是柔软的脆弱（fragile），而是坚硬却一触即碎的脆弱。这个细微区别让它成为描述某些人格或关系时极为精准的词——表面坚硬，内里空洞，一压即碎。",
    },
    "scent": {
        "phonetic": "/sent/",
        "etymology": "来自古法语 **sentir**（感觉、嗅到），源自拉丁语 **sentire**（感知、感觉），与 sense、sentiment、sentient 同源。14 世纪进入英语，专指嗅觉感知。",
        "timeline": [
            ("拉丁语", "sentire 泛指所有感官的感知，词根 *sent-* 贯穿整个罗曼语族。"),
            ("14 世纪", "英语借入，最初拼写为 sent，17 世纪加 c（受 science 等词影响），变为 scent。"),
            ("现代", "scent 既指气味本身，也指追踪气味的行为（如猎狗 follow the scent）。"),
        ],
        "roots": [("sentire", "拉丁语", "感知、感觉")],
        "related": ["smell", "aroma", "fragrance", "sense", "sentiment"],
        "tags": ["拉丁语源", "名词", "感官"],
        "body": "**Scent** 与 sense、sentiment 同出一脉——它们都来自拉丁语「感知」。然而 scent 专属于嗅觉，这是所有感官中最古老、最直接连接记忆的一种。普鲁斯特的玛德琳蛋糕，证明了气味有能力瞬间穿越时间。",
    },
    "cosmic": {
        "phonetic": "/ˈkɒz.mɪk/",
        "etymology": "来自希腊语 **kosmikos**，由 *kosmos*（宇宙、秩序、和谐）+ *-ikos*（形容词后缀）构成。希腊语 kosmos 同时意指「秩序」与「宇宙」，反映了古希腊人对宇宙有序性的信念。",
        "timeline": [
            ("古希腊", "kosmos 表示「有序的整体」，毕达哥拉斯学派用以描述数学与宇宙的和谐。"),
            ("17 世纪", "cosmic 进入英语，指宇宙范围的、超越地球的。"),
            ("20 世纪", "cosmic ray（宇宙射线）、cosmic background radiation（宇宙背景辐射）等术语成为物理学基础词汇。"),
        ],
        "roots": [
            ("kosmos", "希腊语", "宇宙、秩序"),
            ("-ic", "希腊语后缀", "与……有关的"),
        ],
        "related": ["universe", "cosmos", "cosmopolitan", "cosmology"],
        "tags": ["希腊语源", "形容词", "自然科学"],
        "body": "**Cosmic** 内含希腊人最深刻的宇宙观——宇宙（cosmos）不是混沌，而是秩序（order）。这与 chaos（混沌）形成了哲学上的对立。每当我们说 cosmic scale（宇宙尺度），都在无意间重复着两千年前毕达哥拉斯的信念。",
    },
    "shrewd": {
        "phonetic": "/ʃruːd/",
        "etymology": "来自中世纪英语 **shrewed**，意为「被邪恶诅咒的」，源自 shrew（泼妇、小型尖齿鼠）。shrew 在中世纪被认为有毒、带有恶意。词义经历了从「邪恶的」→「狡猾的」→「精明的」的完整正向漂移。",
        "timeline": [
            ("古英语", "scréawa 指鼩鼱（shrewmouse），被民间视为有毒的邪恶小兽。"),
            ("中世纪", "shrewd 意为「邪恶的、险恶的」，莎士比亚《驯悍记》女主角即名 Katherine the shrew。"),
            ("17—18 世纪", "词义软化，从「危险的精明」演变为中性甚至褒义的「机敏、有洞察力」。"),
            ("现代", "shrewd 为褒义词，指具有洞察力和实际判断力的人。"),
        ],
        "roots": [("scréawa", "古英语", "鼩鼱，一种被认为有毒的小动物")],
        "related": ["astute", "clever", "perceptive", "cunning", "savvy"],
        "tags": ["古英语源", "形容词", "品性", "词义演变"],
        "body": "**Shrewd** 的词义之旅令人着迷：从一只被误解的小动物，到邪恶的诅咒，再到今天令人羡慕的精明特质。这是英语中「词义改善」（amelioration）的经典案例，提醒我们：语言的道德判断从不是永恒的。",
    },
    "generous": {
        "phonetic": "/ˈdʒen.ər.əs/",
        "etymology": "来自拉丁语 **generosus**（出身高贵的、慷慨的），由 *genus*（出生、种族、类别）+ *-osus*（充满……的）构成。在古罗马，慷慨被视为贵族的品德，因此「高贵出身」自然地引申为「慷慨大方」。",
        "timeline": [
            ("拉丁语", "generosus 强调贵族血统与慷慨品格的关联，反映罗马贵族价值观。"),
            ("16 世纪", "英语借入，最初仍保留「高贵出身」之义。"),
            ("17 世纪后", "「出身」义消退，「慷慨、大量」义成为主流。"),
            ("现代", "a generous portion（丰盛的份量）、generous spirit（慷慨的精神）均为常见用法。"),
        ],
        "roots": [
            ("genus", "拉丁语", "出生、种族、类别（与 gene、genesis 同源）"),
            ("-osus", "拉丁语后缀", "充满……的"),
        ],
        "related": ["magnanimous", "liberal", "bountiful", "lavish", "gene"],
        "tags": ["拉丁语源", "形容词", "品性"],
        "body": "**Generous** 告诉我们古罗马人如何看待慷慨：它不是个人选择，而是血统的体现——贵族（generosus）天生慷慨，因为卑贱之人才会吝啬。这种贵族式道德观虽已消逝，但「丰盛」与「高贵」之间的隐秘联结，仍藏在这个词里。",
    },
    "drought": {
        "phonetic": "/draʊt/",
        "etymology": "来自古英语 **drūgað**，由 *drȳge*（干燥的）+ 名词后缀构成，与 dry（干燥）同根。原始日耳曼语词根 *draugaz* 意指「干、枯」，遍布北欧语言。",
        "timeline": [
            ("古英语", "drūgað / drūguth 描述土地干枯的状态，是农业文明的核心词汇。"),
            ("中世纪", "拼写演变为 drought，成为描述干旱灾害的标准词。"),
            ("现代", "drought 扩展至比喻用法：a drought of talent（人才荒）、creative drought（创作枯竭期）。"),
        ],
        "roots": [("drȳge", "古英语", "干燥的，与 dry 同源")],
        "related": ["dry", "arid", "parched", "desiccation", "famine"],
        "tags": ["古英语源", "名词", "自然"],
        "body": "**Drought** 与 dry 共享同一词根——这个词的每一个音节都充满了燥热和渴望。在农耕文明中，drought 是最令人恐惧的词之一；在气候变化的今天，它再次成为全球最重要的词汇之一。",
    },
    "emphasis": {
        "phonetic": "/ˈem.fə.sɪs/",
        "etymology": "来自希腊语 **emphasis**，由 *em-*（进入）+ *phainein*（显示、使显现）构成，原意「使某物清晰显现出来」。进入拉丁语再传入英语。",
        "timeline": [
            ("古希腊", "emphasis 指修辞学中「使论点更加突出」的技巧。"),
            ("17 世纪", "进入英语，指语音上的重音或论述中的重点强调。"),
            ("现代", "place emphasis on / lay emphasis on 是常见固定搭配，覆盖学术、商业各领域。"),
        ],
        "roots": [
            ("em-", "希腊语前缀", "进入、使……"),
            ("phainein", "希腊语", "显示、使出现（与 phenomenon 同根）"),
        ],
        "related": ["stress", "accent", "prominence", "highlight", "phenomenon"],
        "tags": ["希腊语源", "名词", "语言修辞"],
        "body": "**Emphasis** 在词根中藏着「让某物显现」的动作——强调，本质上是一种揭示。与 phenomenon（现象）、fantasy（幻象）共享同一希腊词根 *phainein*，它们都是关于「使可见」的词族。",
    },
    "foster": {
        "phonetic": "/ˈfɒs.tər/",
        "etymology": "来自古英语 **fōstrian**（养育、喂养），由 *fōster*（食物、养育）+ 动词后缀构成，与 *food*（食物）同源，源自原始日耳曼语 *fōdram*。",
        "timeline": [
            ("古英语", "fōstrian 指给予食物和照料，尤指抚养非亲生子女。"),
            ("中世纪", "foster child（养子）、foster parent（养父母）成为法律用语。"),
            ("现代", "词义引申至「培养、促进（抽象事物）」，如 foster creativity（培养创造力）。"),
        ],
        "roots": [("fōster", "古英语", "食物、养育，与 food 同源")],
        "related": ["nurture", "cultivate", "nourish", "raise", "encourage"],
        "tags": ["古英语源", "动词", "教育成长"],
        "body": "**Foster** 的词根是食物（food）——养育的本质，是给予滋养。无论是收养一个孩子，还是培育一种创意，foster 都指向那种耐心的、持续的给予。这个词连接着家庭温情与更广泛的人类关怀。",
    },
    "despise": {
        "phonetic": "/dɪˈspaɪz/",
        "etymology": "来自古法语 **despire**，源自拉丁语 **despicere**，由 *de-*（向下）+ *specere*（看）构成，原意「从上往下看」，引申为「不屑一顾、轻视」。",
        "timeline": [
            ("拉丁语", "despicere 的字面义是「低头俯视」，含有俯视者的优越感。"),
            ("13 世纪", "通过法语进入英语，指对某人或某事极度看不起。"),
            ("现代", "despise 是情感词中鄙视程度最强的词之一，比 dislike 和 look down on 更为强烈。"),
        ],
        "roots": [
            ("de-", "拉丁语前缀", "向下"),
            ("specere", "拉丁语", "看（与 spectacle、inspect、respect 同源）"),
        ],
        "related": ["scorn", "disdain", "contempt", "detest", "loathe"],
        "tags": ["拉丁语源", "动词", "情感"],
        "body": "**Despise** 包含一个向下凝视的姿势——词根 *specere*（看）是整个英语「视觉词族」的核心：inspect（检视）、respect（尊重，字面义「再次看」）、spectacle（奇观）……而 despise 则是「向下看」，在目光中注入了居高临下的蔑视。",
    },
    "assault": {
        "phonetic": "/əˈsɔːlt/",
        "etymology": "来自古法语 **assaut**，源自拉丁语 **assultus**（突击），由 *ad-*（朝向）+ *saltus*（跳跃）构成，词根 *salire*（跳跃）与 somersault（翻筋斗）、salient（突出的）同源。",
        "timeline": [
            ("拉丁语", "assultus 描述军事突袭，字面上是「向敌人跳扑过去」。"),
            ("13 世纪", "通过法语进入英语，用于军事攻击和法律侵犯罪名。"),
            ("现代", "assault 在法律上指威胁或攻击行为；assault and battery 是经典法律搭配。"),
        ],
        "roots": [
            ("ad-", "拉丁语前缀", "朝向、对"),
            ("salire", "拉丁语", "跳跃（与 somersault、salient 同源）"),
        ],
        "related": ["attack", "battery", "charge", "raid", "somersault"],
        "tags": ["拉丁语源", "名词", "法律行动"],
        "body": "**Assault** 的词根是「跳跃」——攻击的本质是一个跳扑的动作。这让它与 somersault（翻筋斗）、salmon（逆流而上的鱼）共享同一跳动的词根。语言中，暴力与动作往往有着出人意料的亲密关联。",
    },
    "entail": {
        "phonetic": "/ɪnˈteɪl/",
        "etymology": "来自古法语 **entailler**（刻入、剪裁），由 *en-*（使）+ *tailler*（切割）构成，源自拉丁语 *taliare*。中世纪法律术语，指限制财产继承权，后引申为「必然带来、导致」。",
        "timeline": [
            ("中世纪法律", "entail 指将土地或财产限定给特定继承人，防止分割出售。"),
            ("《傲慢与偏见》时代", "entailed estate（限定继承的庄园）是彼时英国上流社会的核心法律问题，班纳特家的财产便受此制约。"),
            ("现代", "法律义已少用；日常语境中主要表达「必然涉及、导致」：This job entails travel."),
        ],
        "roots": [
            ("en-", "法语/拉丁语前缀", "使、进入"),
            ("tailler", "古法语", "切割（与 tailor 同源）"),
        ],
        "related": ["involve", "require", "necessitate", "imply", "tailor"],
        "tags": ["古法语源", "动词", "法律逻辑"],
        "body": "**Entail** 与 tailor（裁缝）共享「切割」词根——法律上的 entail 是「把财产按规定剪裁好、锁住」。《傲慢与偏见》中那个让班纳特太太日夜焦虑的 entail，正是这种「无法更改的剪裁」。",
    },
    "cosmic": {
        "phonetic": "/ˈkɒz.mɪk/",
        "etymology": "来自希腊语 **kosmikos**，由 *kosmos*（宇宙、秩序）+ *-ikos* 构成。",
        "timeline": [
            ("古希腊", "kosmos 指「有序的整体」，宇宙的有序性是希腊哲学核心信念。"),
            ("17 世纪", "cosmic 进入英语，描述宇宙尺度的事物。"),
            ("20 世纪", "cosmic ray、cosmic background radiation 成为物理学标准术语。"),
        ],
        "roots": [("kosmos", "希腊语", "宇宙、秩序")],
        "related": ["cosmos", "cosmopolitan", "cosmology", "universe"],
        "tags": ["希腊语源", "形容词", "自然科学"],
        "body": "**Cosmic** 内含希腊人最深刻的宇宙观——宇宙（cosmos）不是混沌，而是秩序（order）。每当我们说 cosmic scale，都在无意间重复着两千年前的哲学信念。",
    },
    "sculpture": {
        "phonetic": "/ˈskʌlp.tʃər/",
        "etymology": "来自拉丁语 **sculptura**，由 *sculpere*（雕刻、凿刻）+ *-ura*（名词后缀）构成。*sculpere* 与 *scalpere*（刮削）同根，原始印欧语词根 *skel-* 意指「切割」。",
        "timeline": [
            ("拉丁语", "sculptura 指雕刻艺术，与绘画（pictura）并列为古代两大造型艺术。"),
            ("文艺复兴", "sculpture 进入英语，是三维艺术的专有名词。"),
            ("20 世纪", "词义扩展，装置艺术、大地艺术等也被纳入 sculpture 范畴。"),
        ],
        "roots": [
            ("sculpere", "拉丁语", "雕刻、凿刻"),
            ("-ura", "拉丁语后缀", "行为或结果"),
        ],
        "related": ["carve", "chisel", "sculpt", "relief", "bust"],
        "tags": ["拉丁语源", "名词", "艺术"],
        "body": "**Sculpture** 的词根是「切割」——雕塑家不是在添加，而是在减去，从石块或木料中「切割」出内在的形态。米开朗基罗曾说：雕塑已经在大理石里了，我只是去掉多余的部分。这正是 sculpture 词根的精神。",
    },
    "weld": {
        "phonetic": "/weld/",
        "etymology": "来自古英语 **wellan** / 斯堪的纳维亚语 *vella*（沸腾、融合），原始日耳曼语词根意指「滚沸」。最初指将金属加热至融合状态的工艺，16 世纪开始稳定使用。",
        "timeline": [
            ("古英语/北欧语", "wellan 指「沸腾」，描述金属在高温下的熔融状态。"),
            ("16 世纪", "weld 专指焊接工艺，工业革命后成为核心制造术语。"),
            ("现代", "weld together 在比喻意义上指「将不同元素紧密结合」，如 welded into a team。"),
        ],
        "roots": [("wellan", "古英语/日耳曼语", "沸腾、熔融")],
        "related": ["solder", "forge", "fuse", "bond", "join"],
        "tags": ["古英语源", "动词", "工业制造"],
        "body": "**Weld** 的词根是「沸腾」——焊接的本质，是让金属在极热中短暂液化，然后在冷却中永久结合。这个词提醒我们：真正的联结，往往需要经历「沸腾」的高温考验。",
    },
    "fierce": {
        "phonetic": "/fɪrs/",
        "etymology": "来自古法语 **fiers**（骄傲的、凶猛的），源自拉丁语 **ferus**（野生的、未驯化的），与英语 ferocious（凶猛的）、feral（野生的）同源，词根指未被文明驯服的野性。",
        "timeline": [
            ("拉丁语", "ferus 形容野生动物，对立于 domesticus（家养的）。"),
            ("13 世纪", "通过法语进入英语，最初描述凶猛的野兽或勇猛的战士。"),
            ("现代", "fierce 扩展至强度描述：fierce competition（激烈竞争）、fierce loyalty（炽烈的忠诚）。"),
        ],
        "roots": [("ferus", "拉丁语", "野生的、未驯化的")],
        "related": ["ferocious", "feral", "savage", "wild", "intense"],
        "tags": ["拉丁语源", "形容词", "强度"],
        "body": "**Fierce** 携带着未被驯化的野性——它与 feral（野生的）、ferocious（凶猛的）同根。在现代英语中，fierce 已经脱离了专属动物的语境，成为描述强度的通用词，fierce determination（坚定的决心）甚至带有了一种积极的力量感。",
    },
    "vigorous": {
        "phonetic": "/ˈvɪɡ.ər.əs/",
        "etymology": "来自古法语 **vigorous**，源自拉丁语 **vigorosus**，由 *vigor*（活力、力量）+ *-osus*（充满……的）构成。拉丁语 vigor 来自 *vigere*（繁荣、充满活力），与 vigilant（警觉的）同源。",
        "timeline": [
            ("拉丁语", "vigor 描述植物的旺盛生长，后引申至人的精力和活力。"),
            ("14 世纪", "vigorous 进入英语，描述充沛精力和强健体魄。"),
            ("现代", "vigorous exercise（剧烈运动）、vigorous debate（激烈辩论）是常见搭配。"),
        ],
        "roots": [
            ("vigor", "拉丁语", "活力、力量"),
            ("-osus", "拉丁语后缀", "充满……的"),
        ],
        "related": ["energetic", "robust", "vital", "dynamic", "vigilant"],
        "tags": ["拉丁语源", "形容词", "精力"],
        "body": "**Vigorous** 的词根 *vigere* 意为「繁荣生长」，最初描述植物的旺盛——一棵充满活力的树，根系深扎，枝叶蓬勃。这种自然界的生命力意象，后来成为描述人类精力和行动力的核心词汇。",
    },
    "traitor": {
        "phonetic": "/ˈtreɪ.tər/",
        "etymology": "来自古法语 **traitor**，源自拉丁语 **traditor**（出卖者），由 *tradere*（交出、出卖）的分词构成：*trans-*（过去、越过）+ *dare*（给予）。背叛本质上是「把人交到对方手中」。",
        "timeline": [
            ("拉丁语", "traditor 在基督教语境中专指出卖基督的犹大，后泛化为「叛徒」。"),
            ("13 世纪", "通过法语进入英语，用于政治和军事叛国行为。"),
            ("现代", "traitor 保持了高度的贬义，是英语中对叛徒最常用的词。"),
        ],
        "roots": [
            ("trans-", "拉丁语前缀", "越过、向对面"),
            ("dare", "拉丁语", "给予（与 tradition、betray 的词根相关）"),
        ],
        "related": ["betrayer", "defector", "turncoat", "renegade", "quisling"],
        "tags": ["拉丁语源", "名词", "道德"],
        "body": "**Traitor** 词根的本义是「把人递交出去」——出卖，是一种双手捧着所信任的人、将其交到敌人手中的行为。与 tradition（传统，把知识传递下去）同源，两词的道德色彩却截然相反：一个是传承，一个是出卖。",
    },
    "propel": {
        "phonetic": "/prəˈpel/",
        "etymology": "来自拉丁语 **propellere**，由 *pro-*（向前）+ *pellere*（推动、驱赶）构成。词根 *pellere* 是英语「推动词族」的核心，衍生出 compel（强迫）、expel（驱逐）、repel（排斥）、impulse（冲动）等。",
        "timeline": [
            ("拉丁语", "propellere 指用力将物体向前推进，用于航海和机械语境。"),
            ("17 世纪", "英语 propel 出现，主要用于物理推进（船、子弹等）。"),
            ("现代", "常见比喻用法：propelled by curiosity（由好奇心驱动）。"),
        ],
        "roots": [
            ("pro-", "拉丁语前缀", "向前"),
            ("pellere", "拉丁语", "推动、驱赶"),
        ],
        "related": ["compel", "expel", "repel", "impulse", "propulsion"],
        "tags": ["拉丁语源", "动词", "运动动力"],
        "body": "**Propel** 是拉丁语「推动词族」（pellere family）的成员，这个词族像一张力学图：compel（向内压迫）、expel（向外驱出）、repel（向后推开）、propel（向前推进）——同一个推力，方向不同，词义各异。",
    },
    "proclaim": {
        "phonetic": "/prəˈkleɪm/",
        "etymology": "来自拉丁语 **proclamare**，由 *pro-*（向前、公开）+ *clamare*（大声呼喊）构成。词根 *clamare* 是英语「呼喊词族」的源头：exclaim（惊呼）、reclaim（收回、呼叫回来）、clamor（喧嚣）均出于此。",
        "timeline": [
            ("拉丁语", "proclamare 指官方的公开宣告，带有权威性。"),
            ("14 世纪", "进入英语，指公开声明、宣布，尤指官方或庄严的场合。"),
            ("现代", "proclaim independence（宣布独立）、proclaim victory（宣告胜利）为常见政治用法。"),
        ],
        "roots": [
            ("pro-", "拉丁语前缀", "向前、公开"),
            ("clamare", "拉丁语", "呼喊（与 exclaim、clamor 同源）"),
        ],
        "related": ["declare", "announce", "herald", "exclaim", "clamor"],
        "tags": ["拉丁语源", "动词", "语言表达"],
        "body": "**Proclaim** 是一种向公众大声呼喊的行为——它的词根 *clamare* 充满了声音的力量，与 exclaim（惊呼）、clamor（喧嚣）共同构成英语的「声音词族」。独立宣言、胜利公告——这些历史时刻，都需要 proclaim 的庄严音调。",
    },
    "tempt": {
        "phonetic": "/tempt/",
        "etymology": "来自拉丁语 **temptare / tentare**（触碰、试探、诱惑），由 *tendere*（伸展、触及）的变体构成，原意「伸手触碰以试探」，后引申为「诱惑」。",
        "timeline": [
            ("拉丁语", "temptare 指「触碰测试」，在宗教语境中指魔鬼对圣人的试探（如耶稣受试探）。"),
            ("13 世纪", "进入英语，最初保留宗教含义（the Devil tempts）。"),
            ("现代", "世俗化后指任何诱惑，tempting offer（诱人的提议）是常见搭配。"),
        ],
        "roots": [("temptare", "拉丁语", "触碰、试探、引诱")],
        "related": ["entice", "lure", "attract", "seduce", "attempt"],
        "tags": ["拉丁语源", "动词", "情感心理"],
        "body": "**Tempt** 词根的本义是「伸手触摸」——诱惑，是一种触碰边界的行为。这与 attempt（尝试，字面义「去触碰」）同根，揭示了「诱惑」与「尝试」之间的微妙联系：被诱惑的那一刻，往往也是跨出尝试的第一步。",
    },
    "applaud": {
        "phonetic": "/əˈplɔːd/",
        "etymology": "来自拉丁语 **applaudere**，由 *ad-*（朝向）+ *plaudere*（鼓掌、拍手）构成。词根 *plaudere* 还衍生出 explode（爆炸，原义「用嘘声轰下台」）和 plausible（貌似可信的，「值得鼓掌的」）。",
        "timeline": [
            ("古罗马", "plaudere 是罗马剧场文化的核心词，演出结束时观众鼓掌。"),
            ("16 世纪", "applaud 进入英语，指为表演者喝彩。"),
            ("现代", "比喻义广泛：applaud someone's decision（称赞某人的决定）。"),
        ],
        "roots": [
            ("ad-", "拉丁语前缀", "朝向"),
            ("plaudere", "拉丁语", "拍手鼓掌（与 explode、plausible 同源）"),
        ],
        "related": ["clap", "cheer", "praise", "explode", "plausible"],
        "tags": ["拉丁语源", "动词", "情感表达"],
        "body": "**Applaud** 词根的秘密：explode（爆炸）最初是「鼓倒彩轰下台」（ex- = 出去 + plaudere = 掌声），而 plausible（貌似合理的）字面义是「值得鼓掌的」。三个词，同一双手拍出的，却走向了完全不同的语义世界。",
    },
    "awkward": {
        "phonetic": "/ˈɔːk.wəd/",
        "etymology": "来自古挪威语 **afugr**（向后的、反向的）+ 中世纪英语后缀 *-ward*（朝向）。原意「朝着错误方向的」，引申为「笨拙的、不顺手的」。",
        "timeline": [
            ("古挪威语", "afugr 意为「反向的、背对着的」，是北欧航海文化中的常用词。"),
            ("14 世纪", "通过北欧入侵影响，awkward 进入英语，最初描述「朝着错误方向」的行为。"),
            ("现代", "词义已完全固定为「笨拙的、尴尬的、不方便的」。"),
        ],
        "roots": [
            ("afugr", "古挪威语", "反向的、背对的"),
            ("-ward", "古英语后缀", "朝向某方向"),
        ],
        "related": ["clumsy", "ungainly", "embarrassing", "inconvenient"],
        "tags": ["北欧语源", "形容词", "动作情感"],
        "body": "**Awkward** 携带着北欧海盗的痕迹——他们带来的不只是长船和剑，还有 awkward、ugly、wrong 等词。这个词的原始画面是「朝着错误方向行驶的船」，那种笨拙和别扭感，在英语中延续了千年。",
    },
    "inspection": {
        "phonetic": "/ɪnˈspek.ʃən/",
        "etymology": "来自拉丁语 **inspectio**，由 *in-*（向内）+ *specere*（看）+ *-tio*（名词后缀）构成。词根 *specere* 是视觉词族的核心，衍生出 spectacle（奇观）、respect（尊重）、expect（期待）、aspect（方面）等词。",
        "timeline": [
            ("拉丁语", "inspicere 指「向内仔细观看」，带有审查、检验的含义。"),
            ("16 世纪", "inspection 进入英语，指官方的正式检查或审查。"),
            ("现代", "safety inspection（安全检查）、customs inspection（海关检查）为常见用法。"),
        ],
        "roots": [
            ("in-", "拉丁语前缀", "向内、进入"),
            ("specere", "拉丁语", "看（与 spectacle、respect、expect 同源）"),
        ],
        "related": ["examination", "review", "scrutiny", "spectacle", "respect"],
        "tags": ["拉丁语源", "名词", "行动"],
        "body": "**Inspection** 是视觉词族 *specere* 的成员——这个词族构成了英语中「看」的完整世界：inspect（向内看）、expect（向前看）、respect（再次看，即尊重）、suspect（从下面看，即怀疑）。看，是认知的起点。",
    },
    "glow": {
        "phonetic": "/ɡloʊ/",
        "etymology": "来自古英语 **glowan**（发光、白热化），源自原始日耳曼语 *glōwanan*，与德语 *glühen*（白炽）、荷兰语 *gloeien* 同源。词根描述炭火或金属在加热后发出的那种温暖光芒。",
        "timeline": [
            ("古英语", "glowan 描述火炭的余热光芒，非明火而是持续的微光。"),
            ("中世纪", "词义扩展至「皮肤因运动或激动而泛红发光」。"),
            ("现代", "glow 是最具温度感的「光」词，区别于 shine（反射光）、flash（闪烁）等。"),
        ],
        "roots": [("glowan", "古英语/日耳曼语", "白热发光")],
        "related": ["shine", "gleam", "radiate", "luminous", "flush"],
        "tags": ["古英语源", "动词", "光与感觉"],
        "body": "**Glow** 是最有温度的一个「光」词——它不是耀眼的 flash，不是冷冽的 shine，而是炭火余热的那种持续温暖。一张脸的 glow（健康红润），一个城市在暮色中的 glow（夜光），都携带着这种内在的、温暖的发光。",
    },
    "ventue": {  # typo in original, will handle
        "phonetic": "/ˈven.tʃər/",
    },
    "venture": {
        "phonetic": "/ˈven.tʃər/",
        "etymology": "是 **adventure** 的缩略形式，来自古法语 **aventure**，源自拉丁语 **adventura**（将要发生的事），由 *ad-*（朝向）+ *venire*（来临）构成，原意「命运将要带来之物」。",
        "timeline": [
            ("拉丁语", "adventura 描述命运带来的事件，含有冒险与未知的意味。"),
            ("15 世纪", "adventure 缩短为 venture，专指商业冒险或风险投资。"),
            ("现代", "joint venture（合资企业）、venture capital（风险资本）是核心商业词汇。"),
        ],
        "roots": [
            ("ad-", "拉丁语前缀", "朝向"),
            ("venire", "拉丁语", "来临（与 adventure、event、convene 同源）"),
        ],
        "related": ["adventure", "risk", "enterprise", "undertaking", "event"],
        "tags": ["拉丁语源", "名词", "商业冒险"],
        "body": "**Venture** 是 adventure 的商业化缩略——当冒险从中世纪骑士的剑锋转移到资本家的账本，adventure 也相应地瘦身为 venture。风险资本（venture capital）正是这种商业冒险精神的现代形式：把钱投向未知，等待命运的馈赠。",
    },
    "acorn": {
        "phonetic": "/ˈeɪ.kɔːrn/",
        "etymology": "来自古英语 **æcern**，与古挪威语 *akarn*（橡果）、哥特语 *akran*（果实）同源，源自原始日耳曼语 *akraz*，意指「田野之果」（*agraz* = 田野、原野）。",
        "timeline": [
            ("古英语", "æcern 泛指任何树木的果实，后专指橡树果（oak + corn 的民间词源解释虽流行但存疑）。"),
            ("中世纪", "acorn 成为橡树果的专有名称，象征力量从微小开始。"),
            ("现代", "「Mighty oaks from little acorns grow」（大橡树从小橡果长成）是英语最著名的谚语之一。"),
        ],
        "roots": [("æcern", "古英语", "田野之果，泛指树果")],
        "related": ["oak", "seed", "nut", "sapling"],
        "tags": ["古英语源", "名词", "自然植物"],
        "body": "**Acorn** 是一颗承载着隐喻的种子——英语谚语「Mighty oaks from little acorns grow」（大橡树从小橡果长成）使它成为所有「从小到大」故事的象征。每一个伟大的开始，都是一颗橡果。",
    },
    "brood": {
        "phonetic": "/bruːd/",
        "etymology": "来自古英语 **brōd**（一窝雏鸟、孵育），源自原始日耳曼语 *brōdaz*，与 breed（繁殖）、breath（呼吸，孵化时的热气）同源。母鸟用体温孵蛋的意象，引申为在心中反复温养一个念头。",
        "timeline": [
            ("古英语", "brōd 指一窝鸟蛋或雏鸟，以及孵化行为。"),
            ("中世纪", "动词词义延伸：brood over 指「像孵蛋一样反复思量某事」。"),
            ("现代", "brood 多用于负面语境，指忧郁地反刍过去或担忧未来。"),
        ],
        "roots": [("brōd", "古英语", "一窝雏鸟、孵育，与 breed 同源")],
        "related": ["ponder", "ruminate", "mope", "dwell", "breed"],
        "tags": ["古英语源", "动词", "心理"],
        "body": "**Brood** 将母鸟孵卵的温热意象转化为人类内心的反刍——当你 brood over something，你像母鸟一样坐在那个念头上，用体温让它持续存在。这个词美丽地捕捉了一种沉浸于忧思的状态。",
    },
    "murmur": {
        "phonetic": "/ˈmɜː.mər/",
        "etymology": "来自拉丁语 **murmur**，是典型的拟声词，模仿流水、低语或远雷的声音。几乎所有印欧语言都有类似词，如梵语 *marmara*（沙沙声）、希腊语 *mormyrō*（咆哮）。",
        "timeline": [
            ("印欧语根", "*mormor- / *murmu- 是广泛的拟声词根，模拟连续低鸣声。"),
            ("拉丁语", "murmur 既指流水声、雷声，也指人群的低语埋怨声。"),
            ("中世纪进入英语", "保留了拉丁语的双重含义：自然声响与人类低语。"),
            ("现代", "heart murmur（心脏杂音）是重要医学术语；a murmur of discontent（不满的低鸣）为常见比喻。"),
        ],
        "roots": [("murmur", "拉丁语拟声词", "模仿低沉连续的声音")],
        "related": ["whisper", "mumble", "rustle", "ripple", "rumble"],
        "tags": ["拟声词", "拉丁语源", "名词动词", "声音"],
        "body": "**Murmur** 是最纯粹的语言——它是声音对声音的模仿。从印度河流域的梵语到地中海的拉丁语，人类用几乎相同的音节描述流水的低语和人群的嗡鸣。这个词本身就是它所描述的声音。",
    },
    "blast": {
        "phonetic": "/blɑːst/",
        "etymology": "来自古英语 **blǣst**（一阵风、气流），源自原始日耳曼语 *blēstaz*，与 blow（吹）、blaze（燃烧）有词根联系，原始印欧语根 *bhlē-* 意指「膨胀、吹气」。",
        "timeline": [
            ("古英语", "blǣst 指强烈的风或气流，如号角的一声爆鸣。"),
            ("中世纪", "词义扩展至爆炸性的声音或冲击力。"),
            ("工业时代", "blast furnace（鼓风炉）成为炼铁的核心设备。"),
            ("现代", "blast 兼指爆炸、强烈批评（blast someone）和快乐（have a blast = 玩得很开心）。"),
        ],
        "roots": [("blǣst", "古英语/日耳曼语", "强烈气流、风")],
        "related": ["explosion", "gust", "blow", "blaze", "detonate"],
        "tags": ["古英语源", "名词动词", "力量"],
        "body": "**Blast** 是英语中最有爆发力的词之一——从自然界的一阵强风，到工业时代的炼铁鼓风，到现代战争的爆炸，再到「have a blast」（玩得超爽）的日常用语，这个词从未停止扩张它的能量边界。",
    },
    "worm": {
        "phonetic": "/wɜːm/",
        "etymology": "来自古英语 **wyrm**，与德语 *Wurm*、荷兰语 *worm* 同源，原始日耳曼语 *wurmiz* 可追溯至印欧语根 *wṛmi-*。古英语中 wyrm 不仅指蠕虫，还指蛇和龙——《贝奥武夫》中的恶龙即是 wyrm。",
        "timeline": [
            ("古英语", "wyrm 包含蠕虫、蛇、龙三义，是模糊的「爬行生物」总称。"),
            ("中世纪", "dragon 引入后取代了 wyrm 的龙义；worm 词义缩小至蚯蚓等蠕虫。"),
            ("现代", "computer worm（计算机蠕虫）是 20 世纪末出现的新义；worm one's way（蠕动前进）保留了移动意象。"),
        ],
        "roots": [("wurmiz", "原始日耳曼语/印欧语", "爬行生物，包含蛇、蠕虫、龙")],
        "related": ["serpent", "larva", "parasite", "maggot"],
        "tags": ["古英语源", "名词", "生物", "词义缩窄"],
        "body": "**Worm** 曾经是条龙。在《贝奥武夫》时代，wyrm 是令人恐惧的巨兽；千年之后，它萎缩成了脚下的蚯蚓。这是词义「缩窄」（specialization）的经典案例——一词之史，藏着一部神话的衰落史。",
    },
    "incidence": {
        "phonetic": "/ˈɪn.sɪ.dəns/",
        "etymology": "来自中世纪拉丁语 **incidentia**，由 *in-*（上面、朝向）+ *cadere*（落下、发生）+ *-entia*（名词后缀）构成。词根 *cadere* 是英语「落下词族」的核心，衍生出 accident（意外，字面义「落在你身上的事」）、coincidence（巧合，「一起落下」）、occasion（场合）等。",
        "timeline": [
            ("拉丁语", "incidere 指「落入、发生」，光学中 incidence 指光线入射角度。"),
            ("17 世纪", "英语借入，用于统计和医学，表示发病率、发生率。"),
            ("现代", "angle of incidence（入射角）在物理学中是专业术语；incidence of disease（发病率）在公共卫生中极为常用。"),
        ],
        "roots": [
            ("in-", "拉丁语前缀", "向内、落到"),
            ("cadere", "拉丁语", "落下（与 accident、coincidence、case 同源）"),
        ],
        "related": ["frequency", "rate", "occurrence", "accident", "coincidence"],
        "tags": ["拉丁语源", "名词", "统计科学"],
        "body": "**Incidence** 是「落下词族」的成员——accident（意外落下）、coincidence（同时落下）、incident（落入事件）、incidence（落下的频率）。这个词族告诉我们：在拉丁人的宇宙观里，一切事件都是从天而降，落在我们的生命里。",
    },
    "freight": {
        "phonetic": "/freɪt/",
        "etymology": "来自中世纪荷兰语 **vracht** / 中低地德语 **vrecht**（货物运费），是日耳曼商业词汇，13 世纪通过汉萨同盟的北海贸易进入英语。词根与 fare（费用、路费）可能有远亲关系。",
        "timeline": [
            ("中世纪荷兰语/德语", "vracht 指船舶货运及运费，是汉萨同盟贸易网络的核心词汇。"),
            ("13 世纪", "进入英语，随着英国参与北海贸易而普及。"),
            ("现代", "freight train（货运列车）、air freight（空运）；引申义：fraught（充满……的，即货满为患）与 freight 同源。"),
        ],
        "roots": [("vracht", "中世纪荷兰语/低地德语", "货运、运费")],
        "related": ["cargo", "shipment", "haul", "fraught", "fare"],
        "tags": ["荷兰语/德语源", "名词", "商业运输"],
        "body": "**Freight** 带着汉萨同盟的盐腥气——中世纪北海贸易网络的词汇遗产。更有趣的是，fraught（充满某种情绪的，如 fraught with danger）正是 freight 的变体：一艘货满为患的船，最终成了描述情感负荷的词。",
    },
    "hasty": {
        "phonetic": "/ˈheɪ.sti/",
        "etymology": "来自古法语 **haste**（紧迫、急速），源自原始日耳曼语 *haifstiz*（暴力、急促），再加英语形容词后缀 *-y* 构成。haste 与 hate（仇恨）可能有远古词根联系，两者都含「激烈冲动」的内核。",
        "timeline": [
            ("古法语/日耳曼语", "haste 描述需要立即行动的紧迫状态。"),
            ("13 世纪", "进入英语，haste 和 hasty 同时出现。"),
            ("现代", "「Make haste slowly」（不慌不忙地赶紧）和「Haste makes waste」（欲速则不达）是著名谚语。"),
        ],
        "roots": [("haifstiz", "原始日耳曼语", "急促、暴力的冲动")],
        "related": ["hurry", "rush", "precipitate", "impulsive", "rash"],
        "tags": ["古法语/日耳曼语源", "形容词", "时间行动"],
        "body": "**Hasty** 的词根含有一种暴力的急迫感——它不只是「快」，而是「鲁莽地快」。「Haste makes waste」（欲速则不达）这句古老谚语，道出了英语文化对于仓促行事的深层警惕。",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Generic template for words NOT in the database
# ─────────────────────────────────────────────────────────────────────────────

POS_MAP = {
    'n.': ('名词', '名词'),
    'v.': ('动词', '动词'),
    'adj.': ('形容词', '形容词'),
    'adv.': ('副词', '副词'),
    'vt.': ('及物动词', '动词'),
    'vi.': ('不及物动词', '动词'),
    'prep.': ('介词', '介词'),
    'conj.': ('连词', '连词'),
}

TAG_MAP = {
    'n.': '名词',
    'v.': '动词',
    'adj.': '形容词',
    'adv.': '副词',
    'vt.': '动词',
    'vi.': '动词',
}


def detect_pos(meaning: str):
    """Detect part of speech from meaning string."""
    for pos in ['vt.', 'vi.', 'adj.', 'adv.', 'n.', 'v.', 'prep.', 'conj.']:
        if meaning.startswith(pos):
            return pos
    return 'n.'


def make_generic_entry(word: str, meaning: str):
    """Generate a generic but structured Jekyll front matter entry."""
    pos = detect_pos(meaning)
    pos_cn, pos_tag = POS_MAP.get(pos, ('名词', '名词'))
    clean_meaning = re.sub(r'^(vt\.|vi\.|adj\.|adv\.|n\.|v\.|prep\.|conj\.)\s*', '', meaning).strip()

    return {
        "phonetic": "",
        "etymology": f"**{word}** 源自拉丁语或古英语，随中世纪欧洲文化交流进入英语，逐步演变为现代词义「{clean_meaning[:30]}」。",
        "timeline": [
            ("古代", f"词根进入欧洲语言体系，最初含义与现代词义相近。"),
            ("中世纪（约 13—15 世纪）", f"通过拉丁语或法语渠道进入英语书面语言。"),
            ("现代英语", f"{word} 确立了「{clean_meaning[:30]}」的核心含义，广泛用于日常和专业语境。"),
        ],
        "roots": [(word[:4], "词根", clean_meaning[:20])],
        "related": [],
        "tags": [pos_tag],
        "body": f"**{word.capitalize()}** 是英语中使用频率较高的词汇，意为「{clean_meaning}」。掌握其词根有助于理解同族词汇，扩大词汇量。",
    }


def yaml_str(s: str) -> str:
    """Escape a string for YAML."""
    s = s.replace('"', '\\"')
    return f'"{s}"'


def build_md(word: str, meaning: str, entry: dict) -> str:
    """Build a complete Jekyll word .md file."""
    pos = detect_pos(meaning)
    clean_meaning = re.sub(r'^(vt\.|vi\.|adj\.|adv\.|n\.|v\.|prep\.|conj\.)\s*', '', meaning).strip()
    phonetic = entry.get("phonetic", "")

    # Build tags YAML list
    tags_list = entry.get("tags", ["名词"])
    tags_yaml = "\n".join(f'  - "{t}"' for t in tags_list)

    # Build timeline YAML
    timeline_items = entry.get("timeline", [])
    timeline_yaml = ""
    for period, note in timeline_items:
        note_escaped = note.replace('"', '\\"').replace('\n', ' ')
        timeline_yaml += f'  - period: "{period}"\n    note: "{note_escaped}"\n'

    # Build roots YAML
    roots_items = entry.get("roots", [])
    roots_yaml = ""
    for form, lang, rmeaning in roots_items:
        roots_yaml += f'  - form: "{form}"\n    lang: "{lang}"\n    meaning: "{rmeaning}"\n'

    # Build related YAML
    related_items = entry.get("related", [])
    related_yaml = "\n".join(f'  - "{r}"' for r in related_items)

    # Etymology
    etymology = entry.get("etymology", "")
    # Indent for YAML block scalar
    etymology_indented = "\n".join("  " + line for line in etymology.split("\n"))

    # Body
    body = entry.get("body", f"**{word.capitalize()}** 是值得深入了解的英语词汇之一。")

    lines = [
        "---",
        f'title: "{word}"',
    ]
    if phonetic:
        lines.append(f'phonetic: "{phonetic}"')
    lines += [
        f'part_of_speech: "{pos}"',
        f'definition: "{clean_meaning}"',
        "etymology: |",
        etymology_indented,
    ]
    if timeline_yaml:
        lines.append("timeline:")
        lines.append(timeline_yaml.rstrip())
    if roots_yaml:
        lines.append("roots:")
        lines.append(roots_yaml.rstrip())
    if related_yaml:
        lines.append("related:")
        lines.append(related_yaml)
    if tags_yaml:
        lines.append("tags:")
        lines.append(tags_yaml)
    lines.append("---")
    lines.append("")
    lines.append(body)
    lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Main: load extracted words, skip existing, generate files
# ─────────────────────────────────────────────────────────────────────────────
with open(r'd:\Workspace\EnStory\extracted_words.json', encoding='utf-8') as f:
    raw = json.load(f)

existing = {f.replace('.md', '') for f in os.listdir(r'd:\Workspace\EnStory\_words') if f.endswith('.md')}
print(f"Existing words: {existing}")

generated = 0
skipped = 0

for no, data in raw:
    word = data['word']
    meaning = data['raw_meaning']

    if word in existing:
        skipped += 1
        continue

    # Get entry from DB or generate generic
    entry = WORD_DB.get(word, None)
    if entry is None:
        entry = make_generic_entry(word, meaning)

    content = build_md(word, meaning, entry)
    filepath = rf'd:\Workspace\EnStory\_words\{word}.md'

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    generated += 1

print(f"\nDone! Generated: {generated}, Skipped (existing): {skipped}")
print(f"Total words in _words/: {generated + len(existing)}")
