netcatの実装を考える
===================

- nc-client-thread.py
    - clientをthreadで実装
- nc-client-select.py
    - clientをselectでノンブロッキングで実装
- nc-server-thread.py
    - serverをthreadで実装

thread版は、stdinをblockしてreadしているため、相手側から切断されてもstdinのblockingから抜けるまで終了できない問題あり
(stdinをtimeout付きでreadする方法があればよいがpythonでの実装方法不明)
