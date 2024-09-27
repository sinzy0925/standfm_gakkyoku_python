import sys
import traceback
from playwright.sync_api import sync_playwright
import asyncio
from playwright.async_api import async_playwright
import pygetwindow as gw

testmode = False  # False: 楽曲申請・投稿設定更新する, True: 楽曲申請・投稿設定更新しない
headless_mode = False  # False: 画面あり, True: 画面なし


async def main():
    koumoku = ''
    standfm_id = ''
    standfm_pass = ''
    gakkyoku = ''
    
    if len(sys.argv) > 1:
        koumoku = sys.argv[1]
        #print('koumoku : ' + koumoku)

    if koumoku:
        koumoku_arr = koumoku.split('^')
        
        if koumoku_arr[0]:
            standfm_id = koumoku_arr[0]
        if len(koumoku_arr) > 1:
            standfm_pass = koumoku_arr[1]
        if len(koumoku_arr) > 2:
            gakkyoku = '\n'.join(koumoku_arr[2:]) + '\n'

        print(f'メルアド　　：{standfm_id[:5]}**********')
        print(f'パスワード　：{standfm_pass[:1]}**********')

        for line in gakkyoku.strip().split('\n'):
            if line:
                print(f'作品コード等：{line}')

        print('\nStart::::standfm_login  standfm_login')
        reslogin = 0

        
        timeout = 3000  # 3000ms
        page1 = None
        print('page1 : ', page1)
        res_arr = None
        async with async_playwright() as sp:
            browser = await sp.chromium.launch(headless=headless_mode)
            #context = await browser.new_context()
            
            # 非同期で新しいタブを開く
            page = await browser.new_page()
            #page1 = await context.new_page()
            timeout = 3000  # 3000ms
            res_arr = await standfm_login(headless_mode, standfm_id, standfm_pass,page)


            if res_arr != -1:
                print('standfm_login = OK!')
            else:
                print('standfm_login = NG!')
                print('standfmログイン失敗！ メルアド or パスワード に誤りがあります！')
                reslogin = -1
            
            #browser,context, page2 = res_arr

            gakkyoku_arr = gakkyoku.strip().split('\n')
            gaku_arr = [line.split(',') for line in gakkyoku_arr if line]
            print('gaku_arr : ', gaku_arr)

            res_gakkyokushinsei = ""
            res_gakkyoku2 = []
            samelist_no = True
            go_edit_archive = False
            
            for j, gaku in enumerate(gaku_arr):
                standfm_list_no = str(gaku[1])
                print('standfm_list_no ,j: ', standfm_list_no,j)
                if reslogin == -1:
                    break
                
                JorN1 = gaku[0][0]
                JorN = 'J' if JorN1.isdigit() else 'N'

                if j != 0 and gaku[1] == gaku_arr[j-1][1]:
                    samelist_no = True
                else:
                    samelist_no = False

                if j == len(gaku_arr) - 1 or (j != len(gaku_arr) - 1 and gaku[1] != gaku_arr[j + 1][1]):
                    go_edit_archive = True
                else:
                    go_edit_archive = False

                if JorN == 'J':
                    #print('browser : ', browser)
                    res_gakkyoku = await jasracdata(headless_mode, gaku_arr, j, browser)

                    if res_gakkyoku != -1:
                        if samelist_no:
                            res_gakkyoku2.append(res_gakkyoku)
                        else:
                            res_gakkyoku2 = [res_gakkyoku]

                        print(res_gakkyoku2)
                        print(f'[{standfm_list_no}]配信状況 = 配信OK')
                        print(f'[{standfm_list_no}]JASRACデータ = {res_gakkyoku}')
                    else:
                        print(f'[{standfm_list_no}]配信状況 = 配信NG 配信NG よく確認してください。')
                        print(f'[{standfm_list_no}]JASRACデータ = {res_gakkyoku}')
                    
                    if res_gakkyoku != -1:
                        print('\nStart::::楽曲申請(JASRAC)')
                        
                    
                        res_gakkyokushinsei = await gakkyokushinsei(headless_mode, testmode, gaku_arr, j, res_gakkyoku, res_arr, JorN, standfm_id,page)
                        #if go_edit_archive and res_gakkyokushinsei == 0:
                        #    res_gakkyokushinsei = await gakkyokushinsei2(headless_mode, testmode, gaku_arr, j, res_gakkyoku, res_gakkyoku2, res_arr, JorN, standfm_id,page)

                        if len(gaku_arr) == 1:
                           await browser.close()

                    if res_gakkyokushinsei == 0:
                        print('==================================================')
                        print(f'JASRAC = {res_gakkyoku}')
                        print(f'[OK] [{standfm_list_no}]楽曲申請成功！ = {res_gakkyokushinsei} 楽曲申請成功！')
                        print('==================================================')
                    else:
                        print('==================================================')
                        print(f'JASRAC = {res_gakkyoku}')
                        print(f'[NG] [{standfm_list_no}]楽曲申請失敗！ = {res_gakkyokushinsei} 楽曲申請失敗！失敗！手動で楽曲申請してください！')
                        print('==================================================')

                else:
                    print('\nStart::::NexTone NexTone')
                    #res_gakkyoku = nextonedata(headless_mode, gaku_arr, j)

                    if res_gakkyoku != -1:
                        if samelist_no:
                            res_gakkyoku2.append(res_gakkyoku)
                        else:
                            res_gakkyoku2 = [res_gakkyoku]

                        print(res_gakkyoku2)
                        print('配信状況 = 配信OK')
                        print(f'NexToneデータ = {res_gakkyoku}')
                    else:
                        print('配信状況 = 配信NG 配信NG よく確認してください。')

                    if res_gakkyoku != -1:
                        print('\nStart::::楽曲申請(NexTone)')
                        res_gakkyokushinsei = gakkyokushinsei(headless_mode, testmode, gaku_arr, j, res_gakkyoku, res_arr, JorN, standfm_id)

                        #if go_edit_archive and res_gakkyokushinsei == 0:
                            #res_gakkyokushinsei = gakkyokushinsei2(headless_mode, testmode, gaku_arr, j, res_gakkyoku, res_gakkyoku2, res_arr, JorN, standfm_id)

                        if len(gaku_arr) == 1:
                            await browser.close()

                    if res_gakkyokushinsei == 0:
                        print('==================================================')
                        print(f'NexTone = {res_gakkyoku}')
                        print(f'[OK] [{standfm_list_no}]楽曲申請成功！ = {res_gakkyokushinsei} 楽曲申請成功！')
                        print('==================================================')
                    else:
                        print('==================================================')
                        print(f'NexTone = {res_gakkyoku}')
                        print(f'[NG] [{standfm_list_no}]楽曲申請失敗！ = {res_gakkyokushinsei} 楽曲申請失敗！失敗！手動で楽曲申請してください！')
                        print('==================================================')


async def standfm_login(headless_mode, standfm_id, standfm_pass,page):
    timeout = 1000  # 3000ms
    try:
        #page = await browser.new_page()
        await page.goto('https://stand.fm/')
        await page.set_viewport_size({"width": 800, "height": 800})
        window = gw.getWindowsWithTitle("stand.fm (スタンドエフエム) 音声配信プラットフォーム | stand.fm")[0]
        window.moveTo(0, 0)
        await page.wait_for_timeout(timeout)
        await page.get_by_role("link", name="新規登録・ログイン").click()
        await page.wait_for_timeout(timeout)
        await page.get_by_role("heading", name="ログイン").click()
        for _ in range(3):
            await page.keyboard.press('ArrowDown')
        await page.wait_for_timeout(timeout)
        await page.get_by_placeholder("メールアドレス").click()
        await page.wait_for_timeout(timeout)
        await page.get_by_placeholder("メールアドレス").fill(standfm_id)
        await page.wait_for_timeout(timeout)
        await page.get_by_placeholder("パスワード").fill(standfm_pass)
        await page.wait_for_timeout(timeout)
        await page.get_by_placeholder("パスワード").press("Enter")
        await page.wait_for_timeout(timeout)
        await page.locator('//*[@id="root"]/div/div/div/div/div[1]/div/div[3]/div[3]/div/img').click()
        await page.wait_for_timeout(timeout)
        await page.goto('https://stand.fm/')

        res_arr = page

        return res_arr
    except Exception as e:
        traceback.print_exc()
        return -1
    finally:
        if 'res_arr' not in locals():
            return -1




async def jasracdata(headless_mode, gaku_arr, j, browser):
    timeout = 10000  # 10 seconds
    wtimeout = 2000   # 2 seconds

    page1 = await browser.new_page()
    
    try:
        await page1.goto('https://www2.jasrac.or.jp/eJwid/')
        # ウィンドウのタイトルを取得して位置を変更
        await page1.set_viewport_size({"width": 700, "height": 800})
        window = gw.getWindowsWithTitle("了承画面 | J-WID")[0]
        window.moveTo(0, 0)



        await page1.get_by_role("button", name="上記の内容に了承して 検索に進む").click()
        await page1.wait_for_timeout(1000)
        await page1.evaluate("document.body.style.zoom = '80%'")
        await page1.wait_for_timeout(1000)
        await page1.locator("input[name=\"IN_WORKS_CD\"]").fill(gaku_arr[j][0])
        await page1.wait_for_timeout(1000)
        await page1.keyboard.press('PageDown')
        await page1.wait_for_timeout(1000)
        
        async with page1.expect_popup() as page2_info:
            await page1.locator("input[name=\"IN_WORKS_CD\"]").press("Enter")
        page2 = await page2_info.value
        await page2.wait_for_timeout(2000)
        await page2.set_viewport_size({"width": 700, "height": 800})
        await page2.evaluate("document.body.style.zoom = '80%'")
        await page2.wait_for_timeout(2000)

        await page2.get_by_role("link", name="配信").click()
        await page2.wait_for_timeout(2000)

        await page2.locator('section').filter(has_text='アーティスト名一覧').get_by_role('link').nth(1).click()
        await page2.wait_for_timeout(2000)

        res_text = ""
        res_text += await page2.locator('.detail_iPhone_link').inner_text() + ','  # 作品コード
        res_text += await page2.locator('.baseinfo--name').inner_text() + ','  # 作品名
        #res_text += (await page2.locator('.content-block').nth(21).inner_text().split('\n')[2].split('\t')[1]) + ','  # アーティスト
        ress = await page2.locator('.content-block').nth(21).inner_text()
        ress = ress.split('\n')[2].split('\t')[1] + ','  # アーティスト
        res_text += ress
        
        text2 = await page2.locator('#tab-00-07 > section > div.content > div.PC > table > tbody').inner_text()
        saku_arr = text2.split('\n')
        sakushi = 'なし'
        sakukyoku = 'なし'

        for i in range(2, len(saku_arr)):
            if saku_arr[i].split('\t')[2] == '作詞':
                sakushi = saku_arr[i].split('\t')[1]
                break
        for i in range(2, len(saku_arr)):
            if saku_arr[i].split('\t')[2] == '作曲':
                sakukyoku = saku_arr[i].split('\t')[1]
                break

        res_text += sakushi + ',' + sakukyoku

        #aaa = await page2.query_selector('//*[@id="main_contents"]/main/div[2]/div[2]/dl/dd/ul/li[2]')  # 配信ボタンの色
        #haishinclass = await aaa.inner_html().split('class=')[1].split('"')[1]
        aaa = await page2.locator('#main_contents > main > div.management > div.management-subx4 > dl > dd > ul > li:nth-child(2) > a').get_attribute('class')  # 配信ボタンの色
        haishinclass = aaa

        res_haishin = -1
        haishin = (await page2.locator('.consent').nth(10).inner_text()).split('\n')  # 配信
        if haishin[0] == '配信' and haishin[2] == 'この利用分野は、JASRACが著作権を管理しています。':
            if haishinclass == 'field small purple on':
                res_haishin = 0

        await page1.close()
        await page2.close()

        return res_text if res_haishin == 0 else -1

    except Exception as e:
        traceback.print_exc()
        print("エラー：", str(e))
        return -1



import time
async def gakkyokushinsei(headless_mode, test_mode, gaku_arr, j, res_gakkyoku, res_arr, JorN, standfm_id,page):
    start_time = time.time()  # 開始時間

    timeout = 60  # 秒
    #page2.set_default_timeout(timeout * 1000)  # milliseconds
    #page2.set_default_navigation_timeout(timeout * 1000)  # milliseconds

    gakkyoku_arr = res_gakkyoku.split(',')
    code = gakkyoku_arr[0]
    title = gakkyoku_arr[1]
    artist = gakkyoku_arr[2]
    sakushi = gakkyoku_arr[3]
    sakukyoku = gakkyoku_arr[4]
    standfm_list_no = str(gaku_arr[j][1])

    JASRACorNextone = '-1'
    if JorN == 'J':
        JASRACorNextone = 'JASRAC'
    elif JorN == 'N':
        JASRACorNextone = 'NexTone'
    else:
        print('エラー！！ JASRACかNexToneが分かりません。')

    # 操作の実行
    await page.set_viewport_size({"width": 700, "height": 800})
    window = gw.getWindowsWithTitle("stand.fm (スタンドエフエム) 音声配信プラットフォーム | stand.fm")[0]
    window.moveTo(0, 0)

    await page.get_by_role("img", name="user").click()
    time.sleep(1)
    await page.get_by_role("link", name="放送リスト").click()
    time.sleep(1)
    for i in range(1, int(standfm_list_no)):
        await page.keyboard.press('ArrowDown')
        time.sleep(0.5)  # スリープ

    time.sleep(1)

    xpathh = f'//*[@id="root"]/div/div/div/div/div[2]/div/div[2]/div/div/div[2]/div[1]/div/div[{standfm_list_no}]/div[1]/a/div/div/div[2]/div[1]/div'
    archivename = await page.locator(xpathh).inner_text()


    xpathh = f'//*[@id="root"]/div/div/div/div/div[2]/div/div[2]/div/div/div[2]/div[1]/div/div[{standfm_list_no}]/div[1]/a'
    await page.locator(xpathh).click()
    time.sleep(2)

    xpathh = '//*[@id="root"]/div/div/div/div/div[2]/div[1]/div/div[2]/div/div/div[3]/div/div[1]/div[4]'
    await page.locator(xpathh).click()
    #page3 = await page.wait_for_event('popup')
    time.sleep(2)

    async with page.expect_popup() as page3_info:
        await page.locator('div:nth-child(7) > .css-175oi2r > svg').click()
    page3 = await page3_info.value
    await page3.set_viewport_size({"width": 700, "height": 800})
    

    #await page.locator('div:nth-child(7) > .css-175oi2r > svg').click()
    time.sleep(2)

    if test_mode:
        print(f'testmode 楽曲申請しません！ [{standfm_list_no}] コード[{code}] タイトル[{title}] アーカイブ[{archivename}]')
        await page.close()
        time.sleep(1)
        await page.locator('dialog g path:first-child').click()
    else:
        try:
            time.sleep(1)
            await page3.locator('text=* 必須の質問です').click()
            await page3.keyboard.press('PageDown')
            await page3.keyboard.press('ArrowDown')
            await page3.get_by_role("textbox", name="メールアドレス").click()
            await page3.get_by_role("textbox", name="メールアドレス").fill(standfm_id)
            await page3.get_by_role("heading", name="メールアドレス 必須の質問").click()
            #await page3.locator('input[role="textbox"][name="メールアドレス"]').click()
            #await page3.locator('input[role="textbox"][name="メールアドレス"]').fill(standfm_id)
            #await page3.locator('h1[role="heading"][name="メールアドレス 必須の質問"]').click()
            time.sleep(1)
            await page3.keyboard.press('PageDown')
            await page3.get_by_role("heading", name="権利管理者 必須の質問").click()
            await page3.get_by_text("JASRAC", exact=True).click()
            await page3.get_by_role("button", name="次へ").click()
            #await page3.locator('button[role="button"][name="次へ"]').click()
            time.sleep(2)

            await page3.get_by_role("textbox", name="①作品コード 必須の質問").click()
            await page3.get_by_role("textbox", name="①作品コード 必須の質問").fill(code)
            await page3.get_by_role("heading", name="①作品コード 必須の質問").click()
            time.sleep(2)


            await page3.get_by_role("textbox", name="②作品タイトル 必須の質問").click()
            await page3.get_by_role("textbox", name="②作品タイトル 必須の質問").fill(title)
            await page3.get_by_role("heading", name="②作品タイトル 必須の質問").click()
            time.sleep(2)

            await page3.get_by_role("textbox", name="③アーティスト名 必須の質問").click()
            await page3.get_by_role("textbox", name="③アーティスト名 必須の質問").fill(artist)
            await page3.get_by_role("heading", name="③アーティスト名 必須の質問").click()
            #await page3.keyboard.press('PageDown')
            time.sleep(2)
            await page3.keyboard.press('PageDown')

            await page3.get_by_role("textbox", name="④作詞者 必須の質問").click()
            await page3.get_by_role("textbox", name="④作詞者 必須の質問").fill(sakushi)
            await page3.get_by_role("heading", name="④作詞者 必須の質問").click()
            time.sleep(2)

            await page3.get_by_role("textbox", name="⑤作曲者 必須の質問").click()
            await page3.get_by_role("textbox", name="⑤作曲者 必須の質問").fill(sakukyoku)
            await page3.get_by_role("heading", name="⑤作曲者 必須の質問").click()
            time.sleep(2)

            for _ in range(3):
                await page3.keyboard.press('ArrowDown')
            time.sleep(2)

            await page3.get_by_role("button", name="次へ").click()
            time.sleep(2)
            await page3.get_by_text("* 必須の質問です").click()
            await page3.keyboard.press('PageDown')
            time.sleep(2)

            await page3.get_by_label("回答のコピーを自分宛に送信する").click()
            time.sleep(2)

            await page3.get_by_label("Submit").click()#送信
            #await page3.locator('button[role="button"][name="送信"]').click()
            time.sleep(1)

            # 成功したらクリックできる
            #await page3.get_by_role("heading", name="stand.fm楽曲利用申請").click()#成功したらクリックできる
            time.sleep(1)

            seikou = 0
            #write_log(f'[OK][{standfm_list_no}] コード[{code}] タイトル[{title}] アーカイブ[{archivename}]', seikou)
            print(f'[OK] [{standfm_list_no}] コード[{code}] タイトル[{title}] アーカイブ[{archivename}]')
            await page3.close()
        except Exception as e:
            traceback.print_exc()
            await page3.close()
            seikou = -1
            #write_log(f'[NG][{standfm_list_no}] 楽曲申請失敗 コード[{code}] タイトル[{title}] アーカイブ[{archivename}]', seikou)
            print(f'[NG] [{standfm_list_no}] コード[{code}] タイトル[{title}] アーカイブ[{archivename}]')
            return -1

    return 0    


if __name__ == "__main__":
    asyncio.run(main())
