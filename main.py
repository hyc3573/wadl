import pygame
from pygame.locals import *
from typing import Optional, Callable, Any
from enum import Enum

choseong  =      list('ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ')
jungseong =      list('ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ')
jongseong = ['']+list('ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ')

keys = dict(zip(list('qwertyuiopasdfghjklzxcvbnm') +
                list('QWERTYUIOPASDFGHJKLZXCVBNM'),
                list('ㅂㅈㄷㄱㅅㅛㅕㅑㅐㅔㅁㄴㅇㄹㅎㅗㅓㅏㅣㅋㅌㅊㅍㅠㅜㅡ') +
                list('ㅃㅉㄸㄲㅆㅛㅕㅑㅒㅖㅁㄴㅇㄹㅎㅗㅓㅏㅣㅋㅌㅊㅍㅠㅜㅡ')))

jongtree = {i:i for i in set(keys.values())}
jungtree = {i:i for i in set(keys.values())}

jongtree['ㄱ'] = {'ㅅ':'ㄳ'}
jongtree['ㄴ'] = {'ㅈ':'ㄵ','ㅎ':'ㄶ'}
jongtree['ㄹ'] = {'ㄱ':'ㄺ','ㅁ':'ㄻ','ㅂ':'ㄼ','ㅅ':'ㄽ','ㅌ':'ㄾ','ㅍ':'ㄿ','ㅎ':'ㅀ'}
jongtree['ㅂ'] = {'ㅂ':'ㅄ'}

jungtree['ㅗ'] = {'ㅏ':'ㅘ','ㅐ':'ㅙ','ㅣ':'ㅚ'}
jungtree['ㅜ'] = {'ㅓ':'ㅝ','ㅔ':'ㅞ','ㅣ':'ㅟ'}
jungtree['ㅡ'] = {'ㅣ':'ㅢ'}

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
    return list(filter(lambda x: x is not None, map(hangulCharToJamo, string)))

def qwertyToHangul(string: str) -> list[list[str]]:
    class State(Enum):
        CHO = 0
        JUNG = 1
        JONG = 2
    
    strInd: int = 0
    charInd: int = 0

    state: State = State.CHO
    result: list[list[str]] = [['', '', ''] for _ in string]

    while strInd != len(string):
        char = keys[string[strInd]]
        print(char)

        if state == State.CHO:
            result[charInd][0] = char
            state = State.JUNG
        elif state == State.JUNG:
            if char in jungtree.keys():
                strInd += 1
                result[charInd][1] = jungtree[keys[string[strInd]]]
            else:
                result[charInd][1] = char
            state = State.JONG
        elif state == State.JONG:
            if jongtree[char] is dict:
                strInd += 1
                result[charInd][2] = jongtree[keys[string[strInd]]]
            else:
                result[charInd][2] = char

            result[charInd][2] = char
            state = State.CHO
            charInd += 1
        
        strInd += 1

    return result
    
print(qwertyToHangul('rirehfTidQkfQofx'))

WIDTH = 800
HEIGHT = 700

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('한글 워들')

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return

        screen.fill((0, 0, 0))

        #draw
        
        pygame.display.flip()


if __name__ == '__main__': main()

