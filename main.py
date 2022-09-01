import pygame
from pygame.locals import *
from typing import Optional, Callable, Any, Union, Dict, cast
from enum import Enum, auto
from functools import reduce
from operator import add

jaeum = list('ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ')
moeum = list('ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅛㅜㅠㅡㅣ')

choseong  =      list('ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ')
jungseong =      list('ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ')
jongseong = ['']+list('ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ')

chojong = [''] + list(set(choseong + jongseong))

keys = dict(zip(list('qwertyuiopasdfghjklzxcvbnm') +
                list('QWERTYUIOPASDFGHJKLZXCVBNM'),
                list('ㅂㅈㄷㄱㅅㅛㅕㅑㅐㅔㅁㄴㅇㄹㅎㅗㅓㅏㅣㅋㅌㅊㅍㅠㅜㅡ') +
                list('ㅃㅉㄸㄲㅆㅛㅕㅑㅒㅖㅁㄴㅇㄹㅎㅗㅓㅏㅣㅋㅌㅊㅍㅠㅜㅡ')))

jongcomp = {}
jongcomp.update({'ㄱㅅ':'ㄳ'})
jongcomp.update({'ㄴㅈ':'ㄵ','ㄴㅎ':'ㄶ'})
jongcomp.update({'ㄹㄱ':'ㄺ','ㄹㅁ':'ㄻ','ㄹㅂ':'ㄼ','ㄹㅅ':'ㄽ','ㄹㅌ':'ㄾ','ㄹㅍ':'ㄿ','ㄹㅎ':'ㅀ'})
jongcomp.update({'ㅂㅅ':'ㅄ'})

jungcomp = {}
jungcomp.update({'ㅗㅏ':'ㅘ','ㅗㅐ':'ㅙ','ㅗㅣ':'ㅚ'})
jungcomp.update({'ㅜㅓ':'ㅝ','ㅜㅔ':'ㅞ','ㅜㅣ':'ㅟ'})
jungcomp.update({'ㅡㅣ':'ㅢ'})

def hangulCharToJamo(string: str) -> Optional[list[str]]:
    if len(string) != 1:
        return None
    
    cp = ord(string)

    if 44032 > cp or 55203 < cp:
        return None

    choind  = (cp-44032)//(21*28)
    jungind = (cp-44032-choind*21*28)//28
    jongind = (cp-44032-choind*21*28-jungind*28)

    return [choseong[choind], jungseong[jungind], jongseong[jongind]]

def hangulStrToJamo(string: str) -> list[list[str]]:
    return list(filter(None, map(hangulCharToJamo, string)))

def qwertyToHangul(qwerty: str) -> tuple[list[list[str]], bool]:
    class Jamo(Enum):
        JA = auto()
        MO = auto()

    state = Jamo.JA
    seperation = ['']
    string = map(lambda x: keys[x], qwerty)

    # pass one: seperate jaeum and moeum
    for char in string:
        if state == Jamo.JA and char in jaeum:
            seperation[-1] += char
        elif state == Jamo.JA and char in moeum:
            seperation.append(char)
            state = Jamo.MO
        elif state == Jamo.MO and char in moeum:
            seperation[-1] += char
        else:
            seperation.append(char)
            state = Jamo.JA

    # print(seperation)

    # pass two: seperate jaeum
    state = Jamo.JA
    combined = []
    for i, group in enumerate(seperation):
        if state == Jamo.JA:
            if len(group) == 2:
                if group in jongcomp.keys() and \
                   (i + 1 == len(seperation) or \
                    seperation[i+1][0] in choseong): # ㄱㅅ -> ㄳ, 
                    combined.append(jongcomp[group])
                else:
                    combined += list(group) # ㄱㄱ -> ㄱㄱ
            elif len(group) >= 3:
                if group[:2] in jongcomp.keys(): # ㄱㅅㄱㄱ -> ㄳ ㄱ ㄱ
                    combined.append(jongcomp[group[:2]])
                    combined += list(group[2:])
                else: # ㅇ ㅏ ㄱ ㄱ ㄱ -> 악ㄱㄱ
                    combined += list(group)
            else: # when length of group is 1
                combined.append(group)
        else:
            if len(group) == 2:
                if group in jungcomp.keys(): # ㅗㅐ -> ㅙ
                    combined.append(jungcomp[group])
                else: # ㅐㅐ -> ㅐ ㅐ
                    combined += list(group)
            elif len(group) >= 3:
                if group[:2] in jungcomp.keys(): # ㅗㅐㅐㅐ -> ㅙㅐㅐ
                    combined.append(jungcomp[group[:2]])
                    combined += list(group[2:])
                else: # when length of group is 1
                    combined += list(group)
            else:
                combined.append(group)

        state = Jamo.MO if state == Jamo.JA else Jamo.JA

    # print(combined)

    # pass four: insert empty jongseong
    result = combined[:1]
    if len(combined) >= 3:
        for i in range(1, len(combined)-2):
            result.append(combined[i])
            # not a jaeum
            if combined[i-1] in choseong and \
               combined[i] in jungseong and \
               combined[i+1] not in jongseong:
                result.append('')
            # already consumed jongseong
            if combined[i-1] in choseong and \
               combined[i] in jungseong and \
               combined[i+1] in jongseong and \
               combined[i+2] in jungseong:
                result.append('')

        result += combined[-2:]

    if len(combined) == 2:
        result = combined[:]

    if result[-1] in jungseong:
        result.append('')

    # print(result)

    # pass five: remove lone chracter
    
    nolone = []
    result = ['p'] + result + ['p']
    for i in range(1, len(result)-1):
        if (result[i-1] in choseong and \
            result[i] in jungseong) or \
            result[i] in chojong:
            nolone.append(result[i])

    result = ['p'] + nolone[:] + ['p']
    nolone = []

    for i in range(1, len(result)-1):
        if result[i] in chojong and \
           (result[i-1] in jungseong or \
            result[i+1] in jungseong) or \
            result[i] in jungseong:
            nolone.append(result[i])

        elif result[i+1] == 'p' and \
           result[i] in choseong:
            nolone.append(result[i])

    charFinished = False
            
    if len(nolone) >= 2:
        nolone = nolone if nolone[0] != '' else nolone[1:]
        
    if len(nolone) %3 == 1:
        nolone += ['', '']
    elif len(nolone) %3 == 2:
        nolone.append('')
    else:
        charFinished = True
    # print(nolone)

    return ([[nolone[i], nolone[i+1], nolone[i+2]] for i in range(0, len(nolone), 3)], charFinished) 
    
# print(qwertyToHangul('orrrhooodkssudgktpdyQOfxxxdho'))
# print(qwertyToHangul('rkk'))
# print(qwertyToHangul('rk'))
# print(qwertyToHangul('r'))
# print(qwertyToHangul('OrrO'))
# print(qwertyToHangul('rirehftidQkf'))

WIDTH = 800
HEIGHT = 700

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('한글 워들')

    pygame.key.start_text_input()
    pygame.key.set_repeat(500, 50)

    pygame.font.init()
    font = pygame.font.SysFont("Noto Sans CJK KR BLACK", 50)

    buffer = ''
    string = [] 
    bufferChanged = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    if buffer:
                        buffer = buffer[:-1]
                        if not buffer:
                            string[-1] = ['', '', '']
                    elif string:
                        string = string[:-1]

                    bufferChanged = True
            if event.type == TEXTINPUT:
                if ('a' <= event.text and event.text <= 'z') or \
                   ('A' <= event.text and event.text <= 'Z'):
                    buffer += event.text
                    bufferChanged = True

        if bufferChanged:
            temp, charFinished = qwertyToHangul(buffer)

            if not string:
                string.append(['', '', ''])

            if len(temp) >= 1:
                string[-1] = temp[0]

            if len(temp) == 2:
                string.append(temp[1])
                temp = temp[-1:]
                buffer = buffer[-2:]

            bufferChanged = False
                    
        screen.fill((0, 0, 0))

        text = (reduce(add, reduce(add, string, []), ''))
        #draw
        textDraw = font.render(text, True, (255, 255, 255))
        screen.blit(textDraw, (WIDTH/2, HEIGHT/2))
        
        pygame.display.flip()


if __name__ == '__main__':
    main()

