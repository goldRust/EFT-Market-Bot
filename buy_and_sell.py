import PIL.ImageGrab as IG
from PIL import Image
import os
import mouse
from pytesseract import image_to_string
import pytesseract
from pyautogui import press, hotkey, typewrite
import keyboard
import time
import csv
import cv2
from appJar import gui





# Setting the path for tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract'

# Set resolution variables
width = 1920  #2560
height = 1080 #1440
resolution = (width,height)
left_border = 0

# Globals
inv_squares = 40
tesseract_nums = '-c tessedit_char_whitelist=1234567890₽'
purchased = 0
sold = 0
missed = 0
cost = 0
active_color = (161,159,146)
last_price = 0
ref_count = 0
key_ids = []
items_sold = {}
mechanic_list = []
therapist_list = []
shopping_list = []
profit = 0
junkbox_space =190

with open('mechanic.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        mechanic_list.append(row)
    print(mechanic_list)
mechanic_data = mechanic_list.copy()
mechanic_list.remove(mechanic_list[0])

with open('therapist.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        therapist_list.append(row)
    print(therapist_list)
therapist_data = therapist_list.copy()
therapist_list.remove(therapist_list[0])

with open('shopping_list.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        shopping_list.append(row)
    print(shopping_list)
junkbox_data = shopping_list.copy()
shopping_list.remove(shopping_list[0])

with open('report.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        if row[1].isnumeric():
            items_sold[row[0]] = [int(row[1]),int(round(float((row[2]))))]
        else:
            items_sold[row[0]] =[row[1],row[2]]

class Item:
    def __init__(self, y, info):
        self.y = y
        self.name = info[0]
        self.sale_price = int(info[2])
        self.size = int(info[3])

    def get_uses(self):
        right_click([1200,self.y + 10])
        time.sleep(.1)
        leftClick([1200,self.y-120])
        time.sleep(.1)
        use_im = IG.grab((1645,920,1669,935))
        use_im.save(os.getcwd()+'\\uses.png','PNG')
        use_str = image_to_string(Image.open('uses.png'))[:2]
        if use_str == 'Se':
            self.uses = 50
        elif use_str.isnumeric():
            self.uses = int(use_str)
        else:
            self.uses = 0

        time.sleep(.05)
        check_insp()



    def buy(self):
        global last_price
        global cost
        global purchased
        global inv_squares
        time.sleep(.15)
        leftClick([.9*width,self.y+(.03472*height)])
        time.sleep(.25)

        press('y')
        last_price = self.price
        cost += self.price
        purchased +=1

        time.sleep(.15)
        self.profit = self.sale_price - self.price
        if self.name in items_sold:
            items_sold[self.name][0] += 1
            items_sold[self.name][1] += self.profit
        else:
            items_sold[self.name]=[1,self.profit]

        inv_squares -= self.size

        check_fail()

        print('Purchased '+self.name+ ' for ', self.price,' rubles.\nProfit of ',self.profit)


    def price_grab(self):
        box = (round(.69531*width), self.y, round(.75585*width), self.y + round(.03472*height))
        print(box)
        im = IG.grab(box)
        im.save(os.getcwd() + '\\prices.png', 'PNG')
        image = cv2.imread('prices.png')
        image = cv2.bitwise_not(image)
        image = cv2.resize(image, None, fx=2, fy=2,
                           interpolation=cv2.INTER_CUBIC)  # scale

        price_str = image_to_string(image, config=tesseract_nums).replace(' ', '')
        print(price_str)
        if price_str.isnumeric():
            self.price = int(price_str)
        else:
            self.price = 15000000

        if self.price > self.sale_price*8 and self.price != 15000000:
            if price_str[-1] == '4' or price_str[-1] == '2':
                self.price = int(round((self.price - 4)/10))

        while self.price < 1 / 4 * self.sale_price:
            self.price = self.price * 10

        print(self.price)

def check_active():
    # Check to see if the flea market tab is active.

    tab_img = IG.grab((.617*width, .979*height, .6835*width, .993*height))
    tab_img.save(os.getcwd()+'\\tab.png', 'PNG')
    tab_im = Image.open('tab.png', 'r')
    pixel_list = list(tab_im.getdata())

    while pixel_list[0][0] < 159:
        check_fail()
        leftClick([.617*width, .979*height])
        time.sleep(.5)
        tab_img = IG.grab((.617*width, .979*height, .6835*width, .993*height))
        tab_img.save(os.getcwd() + '\\tab.png', 'PNG')
        tab_im = Image.open('tab.png', 'r')
        pixel_list = list(tab_im.getdata())
        print(active_color)
        print(pixel_list[0])

def check_sort():
    # check to make sure that items are sorted by price from least to greatest
    # Commented out sections checked where it said price - this caused it to be clicked too often. Trying with 'Offer'
    #sort_img = IG.grab((1360,150,1850, 185))
    sort_img = IG.grab((.531*width, .104*height, .5664*width, .125*height))

    sort_img.save(os.getcwd()+'\\sort.png','PNG')
    sort_text = image_to_string(Image.open('sort.png'))

    print(sort_text)
    if sort_text != 'Price «~' and sort_text != 'Offer Pricel¥':

        mouse.move(.703*width,.114*height)
        time.sleep(.3)
        leftClick([.703*width,.114*height])
        time.sleep(.15)

def check_sort_pix():
    time.sleep(.15)
    sort_img = IG.grab((.742*width, .111*height, .75*width,.118*height))
    sort_img.save(os.getcwd()+'\\sort.png','PNG')
    sort_im = Image.open('sort.png', 'r')
    pixel_list = list(sort_im.getdata())

    if pixel_list[30] != (177,183,180) and pixel_list[30] != (178,183,180):
        time.sleep(1)
        sort_img = IG.grab((.742 * width, .111 * height, .75 * width, .118 * height))
        sort_img.save(os.getcwd() + '\\sort.png', 'PNG')
        sort_im = Image.open('sort.png', 'r')
        pixel_list = list(sort_im.getdata())
        print(pixel_list[30])
        if pixel_list[30] != (177,183,180) and pixel_list[30] != (178,183,180):

            mouse.move(.703*width, .114*height)
            time.sleep(.3)
            leftClick([.703*width, .114*height])
            time.sleep(.15)

def refresh():
    # Click the refresh button
    check_active()
    check_insp()
    # check_sort_pix()
    leftClick([.957*width,.107*height])
    check_fail()
    leftClick([.957*width,.107*height])

    time.sleep(1)

def leftClick(loc): # loc is a 2 param list [x,y]
    mouse.move(loc[0], loc[1])
    mouse.click()

def right_click(loc):
    mouse.move(loc[0],loc[1])
    mouse.right_click()

def check_fail():
    global missed
    global purchased
    global cost
    # fail_im = IG.grab((1200,690, 1400,730))
    # fail_im = IG.grab((1100, 690, 1400, 730)) <- This one works
    fail_im = IG.grab((.4296*width, .5*height, .5468*width, .555*height))
    fail_im.save(os.getcwd()+'\\fail_message.png','PNG')
    fail_str = image_to_string(Image.open('fail_message.png'))
    fail_pix = Image.open('fail_message.png', 'r')
    pix_list = list(fail_pix.getdata())




    if pix_list[0] == (0,0,0):
        press('esc')

        missed += 1
        # purchased -= 1
        cost -= last_price
        print('Item Missed')

def check_insp():
    insp_im = IG.grab((.332*width, .2638*height, .421*width,.2777*height))
    insp_im.save(os.getcwd()+'\\insp.png', 'PNG')
    insp_str = image_to_string(Image.open('insp.png'))
    if insp_str == 'EXAMINE: Factory exit key':
        press('esc')

def dealer_page():
    deal_img = IG.grab((.4257*width, .4430*height, .4871*width, .4611*height))
    deal_img.save(os.getcwd() + '\\dealer.png', 'PNG')
    deal_str = image_to_string(Image.open('dealer.png')).replace(' ','')
    if deal_str == 'Therapist':
        return
    while deal_str != 'Therapist':
        check_fail()
        deal_img = IG.grab((.4257*width, .4430*height, .4871*width, .4611*height))
        deal_img.save(os.getcwd() + '\\dealer.png', 'PNG')
        deal_str = image_to_string(Image.open('dealer.png'))
        if deal_str == 'Therapist':
            break
        time.sleep(.15)
        leftClick([.5644*width, .9791*height])
        deal_img = IG.grab((.4257*width, .4430*height, .4871*width, .4611*height))
        deal_img.save(os.getcwd() + '\\dealer.png', 'PNG')
        deal_str = image_to_string(Image.open('dealer.png'))
        print(deal_str)

def therapist():
    print('Getting Therapist')
    mouse.move(.4492*width, .3472*height)
    time.sleep(.5)
    leftClick([.4492*width, .3472*height])
    sell_image = IG.grab((.0691*width, .0847*height, .0707*width, .0881*height))

    sell_image.save(os.getcwd() + '\\sell.png', 'PNG')
    sell_im = Image.open('sell.png', 'r')
    pixel_list = list(sell_im.getdata())
    dot_color = (224,255,109)

    while pixel_list[0][0] < 130:

        mouse.move(.4492*width, .3472*height)
        time.sleep(.5)
        leftClick([.4492*width, .3472*height])
        sell_image = IG.grab((.0691*width, .0847*height, .0707*width, .0881*height))
        sell_image.save(os.getcwd() + '\\sell.png', 'PNG')
        sell_im = Image.open('sell.png', 'r')
        pixel_list = list(sell_im.getdata())

        if pixel_list[0][0] > 130:

            break
        else:
            print(pixel_list)
            dealer_page()
        mouse.move(.4492*width, .3472*height)
        time.sleep(.5)
        leftClick([.4492*width, .3472*height])
        sell_image = IG.grab((.0691*width, .0847*height, .0707*width, .0881*height))
        sell_image.save(os.getcwd() + '\\sell.png', 'PNG')
        sell_im = Image.open('sell.png', 'r')
        pixel_list = list(sell_im.getdata())


    time.sleep(.5)

def skier():
    print('Getting Skier')
    mouse.move(1630, 500)
    time.sleep(.5)
    leftClick([1630, 500])
    sell_image = IG.grab((289, 41, 350, 75))
    sell_image.save(os.getcwd() + '\\sell.png', 'PNG')
    sell_string = image_to_string(Image.open('sell.png')).lower()
    if sell_string == 'sell':
        return
    while sell_string != 'sell':

        mouse.move(1630, 500)
        time.sleep(.5)
        leftClick([1630, 500])
        sell_image = IG.grab((289, 41, 350, 75))
        sell_image.save(os.getcwd() + '\\sell.png', 'PNG')
        sell_string = image_to_string(Image.open('sell.png')).lower()
        if 'sell' in sell_string:
            break
        else:
            print(sell_string)
            dealer_page()
        mouse.move(1630, 500)
        time.sleep(.5)
        leftClick([1630, 500])
        sell_image = IG.grab((289, 41, 350, 75))
        sell_image.save(os.getcwd() + '\\sell.png', 'PNG')
        sell_string = image_to_string(Image.open('sell.png'))

def mechanic():
    print('Getting Mechanic')
    mouse.move(.4570*width, .5555*height)
    time.sleep(.7)
    leftClick([.4570*width, .5555*height])
    sell_image = IG.grab((177, 122, 181, 127))
    sell_image.save(os.getcwd() + '\\sell.png', 'PNG')
    sell_im = Image.open('sell.png', 'r')
    pixel_list = list(sell_im.getdata())

    dot_color = (224, 255, 109)

    while pixel_list[0][0] < 130:
        print(pixel_list[0][0])
        print(pixel_list)
        mouse.move(.4570*width, .5555*height)
        time.sleep(.5)
        leftClick([.4570*width, .5555*height])
        sell_image = IG.grab((.0691*width, .0847*height, .0707*width, .0881*height))
        sell_image.save(os.getcwd() + '\\sell.png', 'PNG')
        sell_im = Image.open('sell.png', 'r')
        pixel_list = list(sell_im.getdata())
        print(pixel_list[0][0])

        if pixel_list[0][0] > 130:

            break
        else:

            dealer_page()
        mouse.move(.4570*width, .5555*height)
        time.sleep(.5)
        leftClick([.4570*width, .5555*height])
        sell_image = IG.grab((.0691*width, .0847*height, .0707*width, .0881*height))
        sell_image.save(os.getcwd() + '\\sell.png', 'PNG')
        sell_im = Image.open('sell.png', 'r')
        pixel_list = list(sell_im.getdata())

    time.sleep(.5)

def sell_items(dealer):

    check_fail()
    global sold
    global items_sold
    print('Selling Items'.center(50,'$'))
    inv_cols = 10
    inv_rows = 4
    start_row = 0
    col_width = .05833*height
    row_height = .05833*height # Probably need a screen shot to refactor for other resolutions

    # Get to the dealer page
    dealer_page()
    # Get to dealer
    dealer()




    # Get sell tab
    time.sleep(.5)
    mouse.move(.1367*width,.041*height)
    time.sleep(.15)
    sale_img = IG.grab((.1367*width, .041*height, .1406*width, .0451*height))
    sale_img.save(os.getcwd()+'\\sale_img.png', 'PNG')
    sale_im = Image.open('sale_img.png','r')
    pix_list = list(sale_im.getdata())

    while pix_list[0][0] < 100:
        dealer()
        leftClick([.1367*width,.041*height])
        sale_img = IG.grab((.1367*width, .041*height, .1406*width, .0451*height))
        sale_img.save(os.getcwd() + '\\sale_img.png', 'PNG')
        sale_im = Image.open('sale_img.png', 'r')
        pix_list = list(sale_im.getdata())

    keys_sold = 0
    y = .2951 * height + (row_height * start_row)
    if y > .9166*height:
        y = .9166*height
    if start_row > 12:
        for r in range(start_row - 12):
            mouse.wheel(-1)
    time.sleep(2)
    keyboard.press('ctrl')
    for row in range(start_row, inv_rows):
        x = .6722*width
        for col in range(inv_cols):
            mouse.move(x,y)
            time.sleep(.05)
            mo_image = IG.grab((x+.005*width,y -.05*height, x + .0625*width, y -.031944*height))
            mo_image.save(os.getcwd()+'\\mo_image.png', 'PNG')
            image = cv2.imread('mo_image.png')
            image = cv2.bitwise_not(image)
            image = cv2.resize(image, None, fx=2, fy=2,
                               interpolation=cv2.INTER_CUBIC)  # scale
            mo_str = image_to_string(image)
            mo_str = mo_str[:8]

            if mo_str == 'Roubles':
                keyboard.release('ctrl')


                time.sleep(.1)
                mouse.drag(x,y-.0104*height,.95*width,.8569*height,duration=.75)
                time.sleep(.2)
                keyboard.press('ctrl')





            # The following adjustment sells EVERYTHING in the first four rows.
            mouse.click()

            time.sleep(.05)
            x += col_width

        if row < 10:
            y += row_height
        elif row == 10:
            y += 70
        elif row > 11:

            mouse.wheel(-1)


        if keyboard.is_pressed('q'):
            finish()

    keyboard.release('ctrl')
    print(keys_sold)
    mouse.move(.4355*width, .16597*height)
    time.sleep(.05)
    mouse.click()

    sold += keys_sold

    with open('report.csv',mode='w') as report_csv:
        report_writer = csv.writer(report_csv, delimiter=',', lineterminator='\n')
        for key, value in items_sold.items():
            report_writer.writerow([key,value[0],value[1]])
            print(key, value)

def browse_market(item_name):
    check_active()
    check_fail()
    mouse.move(.289*width,.1090*height)

    time.sleep(.15)
    mouse.click()
    keyboard.write(' '+item_name,.05)
    keyboard.press('enter')
    mouse.move(.0703*width,.15208*height)
    time.sleep(1)
    mouse.click()
    time.sleep(1)
    found_item = check_name(item_name)
    if found_item == 'Item not found.':
        return 'Skip.'
    if found_item == False:
        dealer_page()
        check_active()
        browse_market(item_name)


def check_char():
    char_img = IG.grab((.3558*width, .0736*height, .4058*width, .0895*height))
    char_img.save(os.getcwd() + '\\dealer.png', 'PNG')
    char_str = image_to_string(Image.open('dealer.png'))
    print(char_str)
    if char_str == 'TACTICAL RIG':
        return True
    else:
        return False

def get_char():
    on_char = check_char()
    while not on_char:

        leftClick((.5066*width, .9854*height))
        time.sleep(.5)
        print('Clicked')
        on_char = check_char()

def to_storage():
    check_fail()
    if not check_char():
        get_char()
    global sold
    global items_sold, inv_squares, junkbox_space
    print('Storing items in junkbox.'.center(50, '*'))
    inv_cols = 10
    inv_rows = 4
    start_row = 0
    col_width = .05833*height
    row_height = .05833*height

    # Get to the character page
    get_char()

    y = .1111*height + (row_height * start_row)
    if y > .9166*height:
        y = .9166*height
    if start_row > 12:
        for r in range(start_row - 12):
            mouse.wheel(-1)
    time.sleep(2)

    for row in range(start_row, inv_rows):
        x = .6722*width
        for col in range(inv_cols):
            mouse.move(x, y)


            time.sleep(.1)
            mouse.drag(x, y - .0104*height, .7148*width, .5138*height, duration=.25)
            time.sleep(.2)
            x += col_width
        y += row_height
    junkbox_space -= 40-inv_squares
    inv_squares = 40

def shop_list(item):
    global purchased, inv_squares

    y = .1388*height
    for x in range(10):
        check_fail()
        new_item = Item(y, item)
        sell_price = int(item[2])

        new_item.price_grab()

        if new_item.price < sell_price:

            if new_item.price > sell_price - 1:
                break
            # new_item.get_uses()

            # if new_item.uses > 48:

            # Commented out to avoid accidental purchases during testing.
            new_item.buy()
            #x -= 1

            print('Update -- Purchased a total of', purchased, 'items for a total of', cost, 'rubles.')
            print('Inventory space remaining: ', inv_squares)
            print('Missed ', missed, ' items.')
            check_fail()
            if inv_squares < 10:
                to_storage()

                break
            check_fail()
            check_active()
            y = .0722*height

        else:
            print('Price is too high. Moving on.')
            break
        y += .0666*height
    check_fail()

def check_market_value(item, dealer):
    global purchased, inv_squares
    global item_list



    y = .1388*height
    for x in range(10):
        check_fail()
        new_item = Item(y, item)
        sell_price = int(item[2])

        new_item.price_grab()

        if new_item.price < sell_price:


            if new_item.price > sell_price - 1:
                break
            # new_item.get_uses()

            # if new_item.uses > 48:

            # Commented out to avoid accidental purchases during testing.
            new_item.buy()
            #x-=1

            print('Update -- Purchased a total of', purchased, 'items for a total of', cost, 'rubles.')
            print('Inventory space remaining: ',inv_squares)
            print('Missed ', missed, ' items.')
            check_fail()
            if inv_squares < 10:
                sell_items(dealer)
                inv_squares = 40
                purchased = 0
                check_active()
                browse_market(item[0])
                check_market_value(item,dealer)

                break
            check_fail()
            check_active()
            #y=104

        else:
            print('Price is too high. Moving on.')
            break
        #y += 96
    check_fail()

    if keyboard.is_pressed('q'):
        finish()

def finish():
    global profit

    print('Sold a total of', sold, 'items')
    print(purchased, 'items remain in the inventory.')
    print('Total profit: ', profit, ' rubles.')
    #exit()

def main():
    active = True
    global purchased,inv_squares
    global missed

    while active:
        check_active()
        check_fail()

        if junkbox_space > 0:
            for item in shopping_list:
                print('Checking '+item[0] + ' --- purchase price: '+ item[2])
                browse_market(item[0])
                shop_list(item)
            to_storage()



        for item in therapist_list:
            print('Checking '+ item[0] + '--- Sale price: ' + item[2])

            browse_market(item[0])
            check_market_value(item, therapist)
            if keyboard.is_pressed('q'):
                active = False
                finish()
        sell_items(therapist)
        inv_squares = 40
        purchased = 0

        for item in mechanic_list:
            print('Checking ' + item[0] + ' --- sales price: ' + item[2])

            browse = browse_market(item[0])
            if browse == 'Skip.':
                continue
            check_market_value(item, mechanic)

            if keyboard.is_pressed('q'):
                active = False
                finish()
        sell_items(mechanic)
        inv_squares = 40
        purchased = 0

def check_name(name):
    count = 0
    name_str = 'noitemname'
    while name[1:5] not in name_str:
        box = (.4902*width, .1388*height, .5937*width, .1597*height)
        im = IG.grab(box)
        im.save(os.getcwd() + '\\name.png', 'PNG')
        image = cv2.imread('name.png')
        image = cv2.bitwise_not(image)
        image = cv2.resize(image, None, fx=2, fy=2,
                           interpolation=cv2.INTER_CUBIC)  # scale

        name_str = image_to_string(image)
        count+=1
        print(name_str)
        if count > 4:
            break

    print(name_str)
    match = 0
    for letter in name:
        if letter in name_str:
            match += 1
        if match >= len(name_str) / 2:
            print('Matched at least half of the letters...')
            return True
    if name[1:5] in name_str:
        print('Name match...')
        return True
    elif name == 'WD-40 400ml':
        return True
    elif 'Sc48e' in name_str:
        return 'Item not found.'
    else:
        return False

def test_sell_loop():
    sell_image = IG.grab((289, 41, 350, 65))
    sell_image.save(os.getcwd() + '\\sell.png', 'PNG')
    sell_string = image_to_string(Image.open('sell.png'))
    print(sell_string)

    ########## MECHANIC PASTED HERE
    for item in mechanic_list:
        print('Checking ' + item[0] + ' --- sales price: ' + item[2])

        browse = browse_market(item[0])
        if browse == 'Skip.':
            continue
        check_market_value(item, mechanic)

        if keyboard.is_pressed('q'):
            active = False
            finish()
    sell_items(mechanic)
    inv_squares = 40
    purchased = 0

def reset_jnk():
    global junkbox_space
    junkbox_space = 190

def gui_man():
    start = gui('Tarkov Market Tool', "600x400", showIcon=False)

    start.addLabel('select_rez','Select your resolution.')
    start.addOptionBox('Resolution',['-Game Resolution-','1920x1080','2560x1440'],colspan=1)
    start.addCheckBox('Junkbox Shopping',3)
    start.addButton('Reset Junkbox',reset_jnk,3)
    start.addTextArea('Instructions',text="Select your resolution, then click START. \nTo stop the bot hit CTRL+ALT+DEL, wait a few moments, then click CANCEL",colspan=2)

    def click_start():
        global width, height, junkbox_space
        res = start.getOptionBox("Resolution")
        if res == '1920x1080':
            width = 1920
            height = 1080
        elif res == '2560x1440':
            width = 2560
            height = 1440
        else:
            print("Resolution not supported.")
            return
        if not start.getCheckBox('Junkbox Shopping'):
            print('No Junkbox Shopping')
            junkbox_space = 0
        main()
    start.startSubWindow('therapist','Therapist Item List')
    start.addTable('Therapist Sale Items',therapist_data)
    start.stopSubWindow()
    start.startSubWindow('mech', 'Mechanic Item List')
    start.addTable('Mechanic Sale Items', mechanic_data)
    start.stopSubWindow()
    start.startSubWindow('jnkbox', 'Junkbox Shopping List')
    start.addTable('Junkbox Items', junkbox_data)
    start.stopSubWindow()
    def show_ther_list():
        start.showSubWindow('therapist')
    def show_mech_list():
        start.showSubWindow('mech')
    def show_junkbox_list():
        start.showSubWindow('jnkbox')
    start.addButtons(['Therapist List','Mechanic List','Junkbox List'], [show_ther_list,show_mech_list,show_junkbox_list])
    start.addButton('Start', click_start)
    start.go()

if __name__ == '__main__':

    gui_man()
