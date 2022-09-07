import pygame
from pygame.locals import *
from typing import Optional, Callable, Any, Union, Dict, Set, cast
from enum import Enum, auto
from functools import reduce
from operator import add
from random import shuffle
from statistics import mean, median, mode, stdev

WIDTH = 800
HEIGHT = 700

FPS = 30

GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (127, 127, 127)

TRIESYPOS = 200
TRIESYOFFSET = 60

jaeum = list('ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ')
moeum = list('ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅛㅜㅠㅡㅣ')

choseong: list  =      list('ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ')
jungseong: list =      list('ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ')
jongseong: list = ['']+list('ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ')

normalJung = list('ㅏㅐㅑㅒㅓㅔㅕㅖㅣ')
bottomJung = list('ㅗㅛㅜㅠㅡ')
doubleJung = list('ㅘㅙㅚㅝㅞㅟㅢ')

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

CHARWIDTH = 100

STRINGX = (WIDTH-CHARWIDTH*3)/2

NORMALJUNGXOFFSET = 30
NORMALJUNGYOFFSET = 0
BOTTOMJUNGXOFFSET = 0
BOTTOMJUNGYOFFSET = 20
DOUBLEJUNGXOFFSET = 10
DOUBLEJUNGYOFFSET = 13

JONGYOFFSET = 40
JONGXOFFSET = 0

CHARHEIGHT = 85
CHAROFFSET = 110

dictionary = []
with open('dict.txt', 'r') as f:
    dictionary = f.readlines()

def jamoToHangulChar(jamo: list[str]) -> str:
    if not jamo[0]:
        return ''
    choIndex = choseong.index(jamo[0])
    if not jamo[1]:
        return jamo[0]
    jungIndex = jungseong.index(jamo[1])
    jongIndex = jongseong.index(jamo[2])

    return chr(0xAC00 + 28 * 21 * choIndex + \
               28 * jungIndex + jongIndex)

def jamoToHangulStr(jamo: list[list[str]]) -> str:
    return ''.join(list(map(jamoToHangulChar, jamo)))

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
    if len(combined) > 3:
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

    if len(combined) == 3:
        if combined[-1] not in jongseong: # ㅇ ㅏ ㅉ -> ㅇㅏ ㅉ
            result = combined[:-1] + ['', combined[-1]]
        else:
            result = combined[:]

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

def check(submit: list[list[str]],
          answer: list[list[str]],
          answerSet: set[str]) -> tuple[list[list[tuple]], bool]:

    result = []
    passed = True
    for i in range(4):
        result.append([])
        for j in range(3):
            if submit[i][j] == answer[i][j]:
                result[i].append(GREEN)
            elif submit[i][j] in answerSet:
                result[i].append(YELLOW)
                passed = False
            else:
                result[i].append(GRAY)
                passed = False

    return (result, passed and len(submit) == len(answer))
    
# print(jamoToHangulStr(qwertyToHangul('orrrhooodkssudgktpdyQOfxxxdho')[0]))
# print(qwertyToHangul('rkk'))
# print(qwertyToHangul('rk'))
# print(qwertyToHangul('r'))
# print(qwertyToHangul('OrrO'))
# print(qwertyToHangul('rirehftidQkf'))

def main():
    tryCnt = []
    
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('한글 워들')

    pygame.key.start_text_input()
    pygame.key.set_repeat(500, 50)

    clock = pygame.time.Clock()

    pygame.font.init()
    font = pygame.font.Font("nanum.ttf", 100)
    sFont = pygame.font.Font("nanum.ttf", 50)

    ansInd = 0
    shuffle(dictionary)
    answer = hangulStrToJamo(dictionary[ansInd])
    answerset = set(reduce(add, answer, []))
    lastPassInd = 0

    buffer = ''
    string = [] 
    bufferChanged = False

    tries = []

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit(0)
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    if buffer:
                        buffer = buffer[:-1]
                        if not buffer:
                            string[-1] = ['', '', '']
                    elif string:
                        string = string[:-1]

                    bufferChanged = True
                if event.key == K_RETURN:
                    if len(string) == 4:
                        result, passed = check(string, answer, answerset)
                        tries.append((string,
                                      result))
                        string = []
                        buffer = ''

                        if passed:
                            # new answer
                            ansInd += 1
                            if ansInd == len(dictionary):
                                shuffle(dictionary)
                                ansInd = 0
                            answer = hangulStrToJamo(dictionary[ansInd])
                            answerset = set(reduce(add, answer, []))

                            # record
                            tryCnt.append(len(tries) - lastPassInd)
                            # print(tryCnt)
                            lastPassInd = len(tries)

                if event.key == K_ESCAPE:
                    # write to file
                    if tryCnt:
                        with open("stat.csv", 'a') as f:
                            sd = stdev(tryCnt) if len(tryCnt) >=2 else -1
                        
                            f.write(f'{mean(tryCnt)},{median(tryCnt)},')
                            f.write(f'{mode(tryCnt)},{sd}\n')

                    # reset
                    return
                    
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
                buffer = buffer[-len(reduce(add, temp[-1], '')):]

            if len(string) > 4:
                string = string[-4:]

            bufferChanged = False

        screen.fill((0, 0, 0))

        for ind in range(max(0, len(tries)-6), len(tries)):
            index = ind - max(0, len(tries)-6)
            for n, i in enumerate(tries[ind][0]):
                c = tries[ind][1][n]
                cho = sFont.render(i[0], True, c[0])
                screen.blit(cho, (STRINGX + CHARWIDTH*n, CHAROFFSET + CHARHEIGHT*index))

                jung = sFont.render(i[1], True, c[1])
                if i[1] in normalJung:
                    screen.blit(jung, (STRINGX + CHARWIDTH*n+NORMALJUNGXOFFSET,
                                       CHAROFFSET + CHARHEIGHT*index + NORMALJUNGYOFFSET))
                elif i[1] in bottomJung:
                    screen.blit(jung, (STRINGX + CHARWIDTH*n+BOTTOMJUNGXOFFSET,
                                       CHAROFFSET + CHARHEIGHT*index + BOTTOMJUNGYOFFSET))
                elif i[1] in doubleJung:
                    screen.blit(jung, (STRINGX + CHARWIDTH*n+DOUBLEJUNGXOFFSET,
                                       CHAROFFSET + CHARHEIGHT*index + DOUBLEJUNGYOFFSET))

                jong = sFont.render(i[2], True, c[2])
                screen.blit(jong, (STRINGX + CHARWIDTH*n+JONGXOFFSET,
                                   CHAROFFSET + CHARHEIGHT*index + JONGYOFFSET))

        text = font.render(jamoToHangulStr(string), True, (255, 255, 255))
        screen.blit(text, ((WIDTH-text.get_rect().width)/2, 0))
       
        pygame.display.flip()

        clock.tick(FPS)


if __name__ == '__main__':
    while True:
        main()

