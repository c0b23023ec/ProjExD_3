import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),  # 右下
    }

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy

        self.dire = (+5, 0)

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
            self.dire = sum_mv
        screen.blit(self.img, self.rct)


class Beam:
    """
    こうかとんが放つビームに関するクラス
    """
    def __init__(self, bird:"Bird"):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん（Birdインスタンス）
        """
        self.img = pg.image.load(f"fig/beam.png")
        self.rct = self.img.get_rect()
        self.vx = bird.dire[0]
        self.vy = bird.dire[1]
        ata = math.atan2(-self.vy, self.vx)
        deg = math.degrees(ata)
        #こうかとんの向きでビームの向きを回転
        self.rotoimg = pg.transform.rotozoom(self.img, deg, 1)
        #ビームの初期位置の調整
        self.rct.centery = bird.rct.centery + (bird.rct.height * self.vy / 5)
        self.rct.centerx = bird.rct.centerx + (bird.rct.width * self.vx / 5)

    def update(self, screen: pg.Surface):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        if check_bound(self.rct) == (True, True):
            self.rct.move_ip(self.vx, self.vy)
            screen.blit(self.rotoimg, self.rct)    


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)
    

class Score:
    """
    スコアに関するクラス
    """
    def __init__(self):
        self.fonto = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.color = (0, 0, 255)
        self.score = 0
        self.img = self.fonto.render("スコア", 0, self.color)
        self.score_rct = self.img.get_rect()
        self.score_rct.center = (100, HEIGHT-50)

    def update(self, screen: pg.Surface):
        """
        爆弾にビームをぶつけた個数に基づいてスコアを増加する
        引数 screen:画面surface 
        """
        self.imgscore = self.fonto.render("スコア:" + str(self.score), 0, self.color)
        screen.blit(self.imgscore, self.score_rct)


class Explosion:
    """
    爆発に関するクラス
    """
    def __init__(self, bomb:"Bomb"):
        """
        爆弾の位置に爆発gifを描画
        引数：爆弾クラス
        """
        self.life = 100
        self.img = pg.image.load(f"fig/explosion.gif")
        self.img_rct = self.img.get_rect()
        self.img_rct.center = bomb.rct.center
    def update(self, screen: pg.Surface):
        """
        爆発をlifeの時間分画像を反転させながら描画する
        引数 screen:画面のSurface
        """
        self.life -= 1
        if self.life > 0:
            if self.life % 2 == 0:
                self.img = pg.transform.flip(self.img, -1, -1)
            screen.blit(self.img, self.img_rct)


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))
    bomb = Bomb((255, 0, 0), 10)
    #beam = None  # Beam(bird)  # ビームインスタンス生成
    # bomb2 = Bomb((0, 0, 255), 20)    
    bombs = [Bomb((255, 0, 0), 10) for i in range(NUM_OF_BOMBS)]
    #explosionリスト初期化
    explosions = []
    beams = []
    score = Score()
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                # スペースキー押下でBeamクラスのインスタンス生成
                #beam = Beam(bird)
                beams.append(Beam(bird))  

        screen.blit(bg_img, [0, 0])
        
        for bomb in bombs:
            if bird.rct.colliderect(bomb.rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                fonto = pg.font.Font(None, 80)
                txt = fonto.render("GameOver", True, (255, 0, 0))
                screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
                bird.change_img(8, screen)
                pg.display.update()
                time.sleep(1)
                return
        
        
        for i, bomb in enumerate(bombs):
            for j, beam in enumerate(beams):
                if beam is not None:
                    if beam.rct.colliderect(bomb.rct):  # ビームが爆弾を撃ち落としたら
                        beams[j] = None
                        bombs[i] = None
                        score.score += 1
                        explosion = Explosion(bomb)
                        explosions.append(explosion)
                        bird.change_img(6, screen)
                        pg.display.update()

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        score.update(screen)
        # beam.update(screen)
        bombs = [bomb for bomb in bombs if bomb is not None]
        beams = [beam for beam in beams if beam is not None]
        for bomb in bombs:
            bomb.update(screen)
        for i, beam in enumerate(beams):
            if check_bound(beam.rct) != (True, True):
                del beams[i]
            else:
                beam.update(screen)
        explosions = [explosion for explosion in explosions if explosion.life > 0]
        for explosion in explosions:
            explosion.update(screen)
        # bomb2.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
