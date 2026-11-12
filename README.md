# 單字開外掛｜Vocab BOOST

單字實力直接升級，學測英文一路破關。

大考中心《高中英文參考詞彙表（111 學年度起適用）》第三至六級 4,008 詞條的背單字遊戲。

- 每日任務、熟練星等（間隔複習 1／2／4／7／15 天）、60 秒閃電戰、真題現場、字卡圖鑑、每日詞表
- 學測頻率：比對 107–115 學年度學測英文試題
- 例句：標「學測原句」者取自大考中心試題；標「編寫例句」者為本站編寫，經老師審閱
- 進度只存在使用者的瀏覽器，可匯出／匯入進度碼

組建：`python -I tools/build_data.py . && node build.js`

## 資料來源與授權

- 第三至六級：大考中心《高中英文參考詞彙表（111 學年度起適用）》，非營利使用並標示出處。
- 歷屆學測試題：大考中心學科能力測驗英文考科（依著作權法第 9 條第 1 項第 5 款，依法令舉行之考試試題不受著作權保護）；參考答案、提示、解析為本站編寫。
- 第七級（進階字彙）：依 wordfreq（Robyn Speer 等，CC BY-SA 4.0）詞頻選出大考詞彙表以外的常用字，再依本站實用度評估挑選排序。此字表（`src/raw/vocab-7.json`）以 CC BY-SA 4.0 釋出。
- 多益職場英文：TOEIC Service List 1.2（Browne, C. & Culligan, B.，CC BY-SA 4.0）中本站沒有的字，經篩選、分組。此字表（`src/raw/vocab-toeic.json`、`src/raw/toeic_tags.json`）以 CC BY-SA 4.0 釋出。
- KK 音標：由 CMU Pronouncing Dictionary（© Carnegie Mellon University，BSD 授權，見 `src/raw/CMUDICT_LICENSE.txt`）轉換並人工校正。
- 例句、中文解釋、閱讀短文、文法卡、解析：本站編寫。插圖為本站以 AI 生成；發音為 Google Cloud Text-to-Speech 產生；背景音樂由程式即時合成。
- 字型：Noto Sans TC、Outfit、Literata（Google Fonts，SIL Open Font License）。

