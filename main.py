from impl.intro import intro
import pygame
from game import Game


def main():
    pygame.init()
    game = Game((1200, 675), 9 / 16)
    game.screen = pygame.display.set_mode(
        game.size, flags=pygame.RESIZABLE | pygame.HWSURFACE)
    pygame.mouse.set_visible(False)

    pygame.display.set_caption('lab01')
    pygame.display.set_icon(pygame.image.load('assets/media/icon.png'))

    intro(game)


if __name__ == "__main__":
    main()
